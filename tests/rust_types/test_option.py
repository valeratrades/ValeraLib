import pytest
from ValeraLib import Option, Some, N, UnwrapOnNone, Ok, Err, Result, UnwrapOnErr, p  # noqa: F401


# Test for Some
def test_some_is_some():
	assert Some(5).is_some() is True


def test_some_is_none():
	assert Some(5).is_none() is False


def test_some_unwrap():
	assert Some(5).unwrap() == 5


def test_some_unwrap_or():
	assert Some(5).unwrap_or(10) == 5


def test_some_map():
	assert Some(5).map(lambda x: x * 2).unwrap() == 10


def test_some_map_or():
	assert Some(5).map_or(0, lambda x: x * 2) == 10


def test_some_map_or_else():
	assert Some(5).map_or_else(lambda: 0, lambda x: x * 2) == 10


def test_some_ok_or():
	assert isinstance(Some(5).ok_or("Error"), Ok)
	assert Some(5).ok_or("Error").unwrap() == 5


def test_some_ok_or_else():
	assert isinstance(Some(5).ok_or_else(lambda: "Error"), Ok)
	assert Some(5).ok_or_else(lambda: "Error").unwrap() == 5


def test_some_or():
	assert Some(5).or_(Some(10)).unwrap() == 5


def test_some_or_else():
	assert Some(5).or_else(lambda: Some(10)).unwrap() == 5


def test_some_replace():
	option = Some(5)
	old_value = option.replace(10)
	assert old_value.unwrap() == 5
	assert option.unwrap() == 10


def test_some_p():
	assert Some(5).p() == 5


# Test for N
def test_none_is_some():
	assert N().is_some() is False


def test_none_is_none():
	assert N().is_none() is True


def test_none_unwrap():
	with pytest.raises(UnwrapOnNone):
		N().unwrap()


def test_none_unwrap_or():
	assert N().unwrap_or(10) == 10


def test_none_map():
	assert isinstance(N().map(lambda x: x * 2), N)


def test_none_map_or():
	assert N().map_or(0, lambda x: x * 2) == 0


def test_none_map_or_else():
	assert N().map_or_else(lambda: 0, lambda x: x * 2) == 0


def test_none_ok_or():
	assert isinstance(N().ok_or("Error"), Err)
	N().ok_or("Error") == Err("Error")


def test_none_ok_or_else():
	assert isinstance(N().ok_or_else(lambda: "Error"), Err)
	with pytest.raises(UnwrapOnErr):
		N().ok_or_else(lambda: "Error").unwrap()


def test_none_or():
	assert N().or_(Some(10)).unwrap() == 10


def test_none_or_else():
	assert N().or_else(lambda: Some(10)).unwrap() == 10


def test_none_replace():
	x = N()
	old = x.replace(10)
	assert isinstance(old, N)
	assert x.unwrap() == 10


def test_none_p():
	@p
	def f():
		N().p()

	with pytest.raises(UnwrapOnErr):
		f().unwrap()
