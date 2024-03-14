import pytest
from ValeraLib import Result, Ok, Err, UnwrapOnErr  # noqa: F401


# Test for Ok
def test_ok_unwrap():
	assert Ok(5).unwrap() == 5


def test_ok_is_ok():
	assert Ok(5).is_ok() is True


def test_ok_is_err():
	assert Ok(5).is_err() is False


def test_ok_map():
	assert Ok(5).map(lambda x: x * 2).unwrap() == 10


def test_ok_map_err():
	assert Ok(5).map_err(lambda x: x * 2).unwrap() == 5  # Error mapper should not be called


def test_ok_or_else():
	result = Ok(5).or_else(lambda x: Err(x))
	assert isinstance(result, Ok)
	assert result.unwrap() == 5


def test_ok_unwrap_or():
	assert Ok(5).unwrap_or(10) == 5


def test_ok_unwrap_or_else():
	assert Ok(2).unwrap_or_else(lambda e: len(e)) == 2


# Test for Err
def test_err_unwrap():
	with pytest.raises(UnwrapOnErr):
		Err("error").unwrap()


def test_err_is_ok():
	assert Err("error").is_ok() is False


def test_err_is_err():
	assert Err("error").is_err() is True


def test_err_map():
	result = Err("error").map(lambda x: x * 2)
	assert isinstance(result, Err)
	with pytest.raises(UnwrapOnErr):
		result.unwrap()


def test_err_map_err():
	result = Err("error").map_err(lambda e: f"new {e}")
	assert isinstance(result, Err)
	with pytest.raises(UnwrapOnErr) as exc_info:
		result.unwrap()
	assert "new error" in str(exc_info.value)


def test_err_or_else():
	result = Err("error").or_else(lambda e: Ok(f"handled {e}"))
	assert isinstance(result, Ok)
	assert result.unwrap() == "handled error"


def test_err_unwrap_or():
	assert Err("error").unwrap_or(10) == 10


def test_err_unwrap_or_else():
	assert Err("foo").unwrap_or_else(lambda e: len(e)) == 3
