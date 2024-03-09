from typing import Generic, TypeVar, Union, Any

T = TypeVar("T")
E = TypeVar("E")


class Ok(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def unwrap(self) -> T:
        return self.value

    def ok_or(self, _or: Any) -> T:
        return self.value

    def is_ok(self) -> bool:
        return True


class Err(Generic[E]):
    def __init__(self, error: E):
        self.error = error

    def unwrap(self):
        raise ValueError(f"Error: {self.error}")

    def ok_or(self, _or: Any) -> Any:
        return _or

    def is_ok(self) -> bool:
        return False


Result = Union[Ok[T], Err[E]]


class Option(Generic[T]):
    def is_some(self) -> bool:
        raise NotImplementedError

    def is_none(self) -> bool:
        raise NotImplementedError

    def unwrap(self) -> T:
        raise NotImplementedError

    def unwrap_or(self, default: T) -> T:
        raise NotImplementedError


class Some(Option[T]):
    def __init__(self, value: T):
        self.value = value

    def is_some(self) -> bool:
        return True

    def is_none(self) -> bool:
        return False

    def unwrap(self) -> T:
        return self.value

    def unwrap_or(self, default: T) -> T:
        return self.value


class N(
    Option[None]
):  # None is named shortly both to avoid conflict with python's None, and to because evokation looks like "N()"; so as to match total number of characters more closely
    def is_some(self) -> bool:
        return False

    def is_none(self) -> bool:
        return True

    def unwrap(self):
        raise ValueError("Tried to unwrap None!")

    def unwrap_or(self, default: T) -> T:
        return default
