# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V. <https://fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""All tests for reuse._comment"""

# pylint: disable=protected-access,invalid-name,redefined-outer-name

from inspect import cleandoc
from textwrap import dedent

import pytest

from reuse._comment import (
    CCommentStyle,
    CommentCreateError,
    CommentParseError,
    CommentStyle,
    HtmlCommentStyle,
    PythonCommentStyle,
    _all_style_classes,
)


@pytest.fixture(
    params=[
        Style for Style in _all_style_classes() if Style.can_handle_single()
    ]
)
def SingleStyle(request):
    """Yield all Style classes that support single-line comments."""
    yield request.param


@pytest.fixture(
    params=[Style for Style in _all_style_classes() if Style.can_handle_multi()]
)
def MultiStyle(request):
    """Yield all Style classes that support multi-line comments."""
    yield request.param


def test_create_comment_generic_single(SingleStyle):
    """Create a comment for all classes that support single-line comments."""
    text = "Hello"
    expected = (
        f"{SingleStyle.SINGLE_LINE}{SingleStyle.INDENT_AFTER_SINGLE}Hello"
    )

    assert SingleStyle.create_comment(text) == expected


def test_create_comment_generic_multi(MultiStyle):
    """Create a comment for all classes that support multi-line comments."""
    # pylint: disable=line-too-long
    text = "Hello"
    expected = cleandoc(
        f"""
        {MultiStyle.MULTI_LINE[0]}
        {MultiStyle.INDENT_BEFORE_MIDDLE}{MultiStyle.MULTI_LINE[1]}{MultiStyle.INDENT_AFTER_MIDDLE}Hello
        {MultiStyle.INDENT_BEFORE_END}{MultiStyle.MULTI_LINE[2]}
        """
    )

    assert MultiStyle.create_comment(text, force_multi=True) == expected


def test_parse_comment_generic_single(SingleStyle):
    """Parse a comment for all classes that support single-line comments."""
    text = f"{SingleStyle.SINGLE_LINE}{SingleStyle.INDENT_AFTER_SINGLE}Hello"
    expected = "Hello"

    assert SingleStyle.parse_comment(text) == expected


def test_parse_comment_generic_multi(MultiStyle):
    """Parse a comment for all classes that support multi-line comments."""
    # pylint: disable=line-too-long
    text = cleandoc(
        f"""
        {MultiStyle.MULTI_LINE[0]}
        {MultiStyle.INDENT_BEFORE_MIDDLE}{MultiStyle.MULTI_LINE[1]}{MultiStyle.INDENT_AFTER_MIDDLE}Hello
        {MultiStyle.INDENT_BEFORE_END}{MultiStyle.MULTI_LINE[2]}
        """
    )
    expected = "Hello"

    assert MultiStyle.parse_comment(text) == expected


def test_base_class_throws_errors():
    """When trying to do much of anything with the base class, expect errors."""
    with pytest.raises(CommentParseError):
        CommentStyle.parse_comment("hello")
    with pytest.raises(CommentCreateError):
        CommentStyle.create_comment("hello")
    with pytest.raises(CommentParseError):
        CommentStyle.comment_at_first_character("hello")


def test_create_comment_python():
    """Create a simple Python comment."""
    text = cleandoc(
        """
        Hello

        world
        """
    )
    expected = cleandoc(
        """
        # Hello
        #
        # world
        """
    )

    assert PythonCommentStyle.create_comment(text) == expected


def test_parse_comment_python():
    """Parse a simple Python comment."""
    text = cleandoc(
        """
        # Hello
        #
        # world
        """
    )
    expected = cleandoc(
        """
        Hello

        world
        """
    )

    assert PythonCommentStyle.parse_comment(text) == expected


def test_parse_comment_python_indented():
    """Preserve indentations in Python comments."""
    text = cleandoc(
        """
        # def foo():
        #     print("foo")
        """
    )
    expected = cleandoc(
        """
        def foo():
            print("foo")
        """
    )

    assert PythonCommentStyle.parse_comment(text) == expected


def test_create_comment_python_dont_strip_newlines():
    """Include newlines in the comment."""
    text = "\nhello\n"
    expected = cleandoc(
        """
        #
        # hello
        #
        """
    )

    assert PythonCommentStyle.create_comment(text) == expected


def test_create_comment_python_force_multi():
    """Raise CommentCreateError when creating a multi-line Python comment."""
    with pytest.raises(CommentCreateError):
        PythonCommentStyle.create_comment("hello", force_multi=True)


def test_parse_comment_python_fail_on_newline():
    """If a provided comment does not start with the comment character, fail."""
    text = dedent(
        """

        #
        # hello
        #

        """
    )
    with pytest.raises(CommentParseError):
        assert PythonCommentStyle.parse_comment(text)


def test_parse_comment_python_not_a_comment():
    """Raise CommentParseError when a comment isn't provided."""
    text = "Hello world"

    with pytest.raises(CommentParseError):
        PythonCommentStyle.parse_comment(text)


def test_parse_comment_python_single_line_is_not_comment():
    """Raise CommentParseError when a single line is not a comment."""
    text = cleandoc(
        """
        # Hello
        world
        """
    )

    with pytest.raises(CommentParseError):
        PythonCommentStyle.parse_comment(text)


def test_parse_comment_python_multi_error():
    """Raise CommentParseError when trying to parse a multi-line Python
    comment.
    """
    with pytest.raises(CommentParseError):
        PythonCommentStyle._parse_comment_multi("Hello world")


def test_create_comment_c_single():
    """Create a C comment with single-line comments."""
    text = cleandoc(
        """
        Hello
        world
        """
    )
    expected = cleandoc(
        """
        // Hello
        // world
        """
    )

    assert CCommentStyle.create_comment(text) == expected


def test_parse_comment_c_single():
    """Parse a C comment with single-line comments."""
    text = cleandoc(
        """
        // Hello
        // world
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_create_comment_c_multi():
    """Create a C comment with multi-line comments."""
    text = cleandoc(
        """
        Hello
        world
        """
    )
    expected = cleandoc(
        """
        /*
         * Hello
         * world
         */
        """
    )

    assert CCommentStyle.create_comment(text, force_multi=True) == expected


def test_create_comment_c_multi_empty_newlines():
    """Create a C comment that contains empty lines."""
    text = cleandoc(
        """
        Hello

        world
        """
    )
    expected = cleandoc(
        """
        /*
         * Hello
         *
         * world
         */
        """
    )

    assert CCommentStyle.create_comment(text, force_multi=True) == expected


def test_create_comment_c_multi_surrounded_by_newlines():
    """Create a C comment that is surrounded by empty lines."""
    text = "\nHello\nworld\n"
    expected = cleandoc(
        """
        /*
         *
         * Hello
         * world
         *
         */
        """
    )

    assert CCommentStyle.create_comment(text, force_multi=True) == expected


def test_create_comment_c_multi_contains_ending():
    """Raise CommentCreateError when the text contains a comment ending."""
    text = cleandoc(
        """
        Hello
        world
        */
        """
    )

    with pytest.raises(CommentCreateError):
        CCommentStyle.create_comment(text, force_multi=True)


def test_parse_comment_c_multi():
    """Parse a C comment with multi-line comments."""
    text = cleandoc(
        """
        /*
         * Hello
         * world
         */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )
    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_missing_middle():
    """Parse a C comment even though the middle markers are missing."""
    text = cleandoc(
        """
        /*
        Hello
        world
        */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_misaligned_end():
    """Parse a C comment even though the end is misaligned."""
    text = cleandoc(
        """
        /*
         * Hello
         * world
        */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected

    text = cleandoc(
        """
        /*
         * Hello
         * world
          */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_no_middle():
    """Parse a C comment that has no middle whatsoever."""
    text = cleandoc(
        """
        /* Hello
         * world */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_ends_at_last():
    """Parse a C comment that treats the last line like a regular line."""
    text = cleandoc(
        """
        /*
         * Hello
         * world */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_starts_at_first():
    """Parse a C comment that treats the first line like a regular line."""
    text = cleandoc(
        """
        /* Hello
         * world
         */
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_indented():
    """Preserve indentations in C comments."""
    text = cleandoc(
        """
        /*
         * Hello
         *   world
         */
        """
    )
    expected = cleandoc(
        """
        Hello
          world
        """
    )

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_single_line():
    """Parse a single-line multi-line comment."""
    text = "/* Hello world */"
    expected = "Hello world"

    assert CCommentStyle.parse_comment(text) == expected


def test_parse_comment_c_multi_no_start():
    """Raise CommentParseError when there is no comment starter."""
    text = "Hello world */"

    with pytest.raises(CommentParseError):
        CCommentStyle.parse_comment(text)

    with pytest.raises(CommentParseError):
        CCommentStyle._parse_comment_multi(text)


def test_parse_comment_c_multi_no_end():
    """Raise CommentParseError when there is no comment end."""
    text = "/* Hello world"

    with pytest.raises(CommentParseError):
        CCommentStyle.parse_comment(text)


def test_parse_comment_c_multi_text_after_end():
    """Raise CommentParseError when there is stuff after the comment
    delimiter.
    """
    text = cleandoc(
        """
        /*
         * Hello
         * world
         */ Spam
        """
    )

    with pytest.raises(CommentParseError):
        CCommentStyle.parse_comment(text)


def test_create_comment_html():
    """Create an HTML comment."""
    text = cleandoc(
        """
        Hello
        world
        """
    )
    expected = cleandoc(
        """
        <!--
        Hello
        world
        -->
        """
    )

    assert HtmlCommentStyle.create_comment(text) == expected


def test_parse_comment_html():
    """Parse an HTML comment."""
    text = cleandoc(
        """
        <!--
        Hello
        world
        -->
        """
    )
    expected = cleandoc(
        """
        Hello
        world
        """
    )

    assert HtmlCommentStyle.parse_comment(text) == expected


def test_create_comment_html_single():
    """Creating a single-line HTML comment fails."""
    with pytest.raises(CommentCreateError):
        HtmlCommentStyle._create_comment_single("hello")


def test_parse_comment_html_single_line():
    """Parse a single-line HTML comment."""
    text = "<!-- Hello world -->"
    expected = "Hello world"

    assert HtmlCommentStyle.parse_comment(text) == expected


def test_comment_at_first_character_python():
    """Find the comment block at the first character."""
    text = cleandoc(
        """
        # Hello
        # world
        Spam
        """
    )
    expected = cleandoc(
        """
        # Hello
        # world
        """
    )

    assert PythonCommentStyle.comment_at_first_character(text) == expected


def test_comment_at_first_character_python_no_comment():
    """The text does not start with a comment character."""
    with pytest.raises(CommentParseError):
        PythonCommentStyle.comment_at_first_character(" # Hello world")


def test_comment_at_first_character_python_indented_comments():
    """Don't handle indented comments."""
    text = cleandoc(
        """
        # Hello
          # world
        """
    )
    expected = "# Hello"

    assert PythonCommentStyle.comment_at_first_character(text) == expected


def test_comment_at_first_character_c_multi():
    """Simple test for a multi-line C comment."""
    text = cleandoc(
        """
        /*
         * Hello
         * world
         */
        Spam
        """
    )
    expected = cleandoc(
        """
        /*
         * Hello
         * world
         */
        """
    )

    assert CCommentStyle.comment_at_first_character(text) == expected


def test_comment_at_first_character_c_multi_never_ends():
    """Expect CommentParseError if the comment never ends."""
    text = cleandoc(
        """
        /*
         * Hello
         * world
        /*
        """
    )

    with pytest.raises(CommentParseError):
        CCommentStyle.comment_at_first_character(text)
