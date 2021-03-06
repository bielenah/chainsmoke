"""
Tests for the common library functions.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
import pytest

from chainsmoke.railroad import railroad_it, Maybe, Either, Error, Just, Nothing
from chainsmoke.chain import chain, compose

eitherable = railroad_it(Either)
maybeable = railroad_it(Maybe)
eitherable_debug = railroad_it(Either, debug=True)
maybeable_debug = railroad_it(Maybe, debug=True)


class ChainSmokeSpecialTestError(Exception):
    pass


class NonValidRailroadType(object):
    pass


def function_that_raises_an_exception():
    raise ChainSmokeSpecialTestError("This magical function raised an exception.")


@eitherable
def add_2_to_either(either):
    return either + 2


@eitherable
def add_3_to_either(either):
    return either + 3


@eitherable
def add_4_to_either(either):
    return either + 4


@eitherable
def function_that_calls_a_function_that_raises_exception(either):
    result = function_that_raises_an_exception()
    return either + result


@maybeable
def add_2_to_maybe(maybe):
    return maybe + 2


@maybeable
def add_3_to_maybe(maybe):
    return maybe + 3


@maybeable
def function_that_calls_a_function_that_raises_exception_maybe(maybe):
    result = function_that_raises_an_exception()
    return maybe + result


@eitherable_debug
def debug_add2(either):
    return either + 2


@eitherable_debug
def debug_add3(either):
    return either + 3


@eitherable_debug
def debug_call_exception_function(either):
    result = function_that_raises_an_exception()
    return either + result


@eitherable_debug
def debug_add4(either):
    return either + 4


@maybeable_debug
def maybe_debug_add2(maybe):
    return maybe + 2


@maybeable_debug
def maybe_debug_add3(maybe):
    return maybe + 3


@maybeable_debug
def maybe_debug_call_exception_function(maybe):
    result = function_that_raises_an_exception()
    return maybe + result


@maybeable_debug
def maybe_debug_add4(maybe):
    return maybe + 4


def test_that_call_chain_returns_15_when_value_is_good():
    func_chain = [
        add_3_to_either,
        add_4_to_either
    ]
    result = compose(*func_chain)(add_2_to_either(6))
    assert result.value == 15


def test_that_call_chain_returns_not_a_number_when_value_is_error():
    func_chain = [
        add_2_to_either("abc"),
        add_3_to_either,
        add_4_to_either
    ]
    result = chain(*func_chain)
    assert isinstance(result.value, TypeError)


def test_that_call_chain_returns_an_error_when_calling_exception_raising_function():
    func_chain = [
        add_2_to_either(2),
        add_3_to_either,
        function_that_calls_a_function_that_raises_exception,
        add_4_to_either
    ]

    result = chain(*func_chain)
    assert isinstance(result, Error)


def test_that_call_returns_a_just_when_value_is_good():
    func_chain = [
        3,
        add_2_to_maybe,
        add_3_to_maybe
    ]
    result = chain(*func_chain)
    assert isinstance(result, Just)
    assert result.value == 8


def test_that_call_returns_a_nothing_value_is_bad():
    func_chain = [
        3,
        add_2_to_maybe,
        function_that_calls_a_function_that_raises_exception_maybe,
        add_3_to_maybe
    ]
    result = chain(*func_chain)
    assert isinstance(result, Nothing)


def test_that_debug_mode_works_with_either():
    with pytest.raises(ChainSmokeSpecialTestError) as exception_info:
        func_chain = [
            debug_add2(2),
            debug_add3,
            debug_call_exception_function,
            debug_add4
        ]
        chain(*func_chain)

    assert exception_info.value.args[0] == 'This magical function raised an exception.'


def test_that_debug_mode_works_with_maybe():
    with pytest.raises(ChainSmokeSpecialTestError) as exception_info:
        func_chain = [
            maybe_debug_add2(2),
            maybe_debug_add3,
            maybe_debug_call_exception_function,
            maybe_debug_add4
        ]
        chain(*func_chain)

    assert exception_info.value.args[0] == 'This magical function raised an exception.'


def test_that_exception_is_raised_when_incorrect_type_is_passed_to_railroad():
    with pytest.raises(TypeError) as exception_info:
        railroad_it(NonValidRailroadType)

    assert exception_info.value.args[0] == 'NonValidRailroadType is not a valid railroad type; try Either or Maybe.'
