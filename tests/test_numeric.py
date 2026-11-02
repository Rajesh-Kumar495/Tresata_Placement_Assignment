from decimal import Decimal

import pytest

from ngr.numeric import looks_like_year, parse_number


@pytest.mark.parametrize(
    "raw, value, decimals",
    [
        ("1,234", Decimal(1234), 0),
        ("(1,234)", Decimal(-1234), 0),
        ("$(1,234)", Decimal(-1234), 0),
        ("$ (1,234)", Decimal(-1234), 0),
        ("−1,234", Decimal(-1234), 0),  # unicode minus
        ("-12.5", Decimal("-12.5"), 1),
        ("0.45", Decimal("0.45"), 2),
        ("$0.82", Decimal("0.82"), 2),
        ("12.5%", Decimal("12.5"), 1),
        ("(3.5)%", Decimal("-3.5"), 1),
        ("1,234(a)", Decimal(1234), 0),
        ("1,234 (1)", Decimal(1234), 0),
        ("4,370*", Decimal(4370), 0),
        ("1,036 ", Decimal(1036), 0),  # nbsp
    ],
)
def test_parse_values(raw, value, decimals):
    p = parse_number(raw)
    assert p.value == value
    assert p.decimals == decimals


@pytest.mark.parametrize("raw", ["—", "–", "-", "$—", "$ —"])
def test_dash_is_zero(raw):
    p = parse_number(raw)
    assert p.value == 0 and p.is_dash


def test_footnote_recorded():
    assert parse_number("1,234(a)").footnotes == ["a"]
    assert parse_number("(12)").footnotes == []  # a paren negative is not a footnote


@pytest.mark.parametrize("raw", ["Net income", "n/m", "NM", "", "Three Months Ended", "$"])
def test_non_numeric(raw):
    assert parse_number(raw).value is None


def test_percent_and_currency_flags():
    assert parse_number("12.5%").is_percent
    assert parse_number("$1").is_currency


def test_unit_of_last_digit():
    assert parse_number("12.3").unit == Decimal("0.1")
    assert parse_number("1,234").unit == Decimal(1)


def test_year_detection():
    assert looks_like_year(parse_number("2026"))
    assert not looks_like_year(parse_number("2,026"))
    assert not looks_like_year(parse_number("$2026"))
