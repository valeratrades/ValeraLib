from dataclasses import dataclass
from typing import Generic, TypeVar, Any, ContextManager, Union, NoReturn
from functools import wraps
from threading import Lock
import contextlib


# Result
# ==============================================================================
T = TypeVar("T")
E = TypeVar("E")


def p(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except UnwrapOnErr as e:
			raise e
		except UnwrapOnNone as e:
			raise e
		except Exception as e:
			return Err(e)

	return wrapper


class UnwrapOnErr(ValueError):
	def __init__(self, additional_info=None):
		message = "Called `unwrap()` on an `Err` value"
		if additional_info is not None:
			message += f"\n{additional_info}"
		super().__init__(message)


class Result(Generic[T, E]):
	def unwrap(self) -> T:
		raise NotImplementedError

	def ok_or(self, _or: Any) -> T:
		raise NotImplementedError

	def is_ok(self) -> bool:
		raise NotImplementedError

	def p(self) -> Union[T, NoReturn]:
		"""
		Propagate the error or unwrap the value.

		----------------
		To propagate, call .p() on the Result[T, E] and annotate the function with @p. It will run the function in a try-except block and return any errors except for UnwrapOnErr and UnwrapOnNone, defined in this module.
		"""
		raise NotImplementedError


class Ok(Result[T, E]):
	def __init__(self, value: T):
		self.value = value

	def unwrap(self) -> T:
		return self.value

	def ok_or(self, _or: Any) -> T:
		return self.value

	def is_ok(self) -> bool:
		return True

	def p(self) -> T:
		return self.value

	def __str__(self) -> str:
		return f"Ok[{self.value}]"


class Err(Result[T, E]):
	def __init__(self, error: E):
		self.error = error

	def unwrap(self):
		raise UnwrapOnErr(f"{type(self.error).__name__}: {self.error}")  # TODO!: exclude this from traceback

	def ok_or(self, _or: Any) -> Any:
		return _or

	def is_ok(self) -> bool:
		return False

	def p(self) -> NoReturn:
		raise self.error

	def __str__(self) -> str:
		return f'Err[{type(self.error).__name__}["{self.error}"]]'


# Option
# ==============================================================================
class UnwrapOnNone(ValueError):
	def __init__(self, additional_info=None):
		message = "Called `unwrap()` on an `None` value."
		if additional_info is not None:
			message += f"\n{additional_info}"
		super().__init__(message)


class Option(Generic[T]):
	def is_some(self) -> bool:
		raise NotImplementedError

	def is_none(self) -> bool:
		raise NotImplementedError

	def unwrap(self) -> T:
		raise NotImplementedError

	def unwrap_or(self, default: T) -> T:
		raise NotImplementedError

	def p(self) -> Union[T, NoReturn]:
		"""
		Propagate the error or unwrap the value.

		----------------
		To proagate, call .p() on the Option[object] and annotate the function with @p. It will run the function in a try-except block and return any errors except for UnwrapOnErr and UnwrapOnNone, defined in this module.
		"""
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

	def p(self) -> T:
		return self.value


class N(Option[None]):  # None is named shortly both to avoid conflict with python's None, and to because evokation looks like "N()"; so as to match total number of characters more closely
	def is_some(self) -> bool:
		return False

	def is_none(self) -> bool:
		return True

	def unwrap(self):
		raise UnwrapOnNone  # TODO!: exclude this from traceback

	def unwrap_or(self, default: T) -> T:
		return default

	def p(self) -> NoReturn:
		raise RuntimeError("Called `unwrap()` on an `None` value.")


# Mutex
# ==============================================================================
T = TypeVar("T")


@dataclass
class Mutex(Generic[T]):
	__value: T
	__lock: Lock
	__dropped: bool = False
	"""
		Rust-like Mutex with lock guarantees

		----------------
		Usage:
		```python
			# Create a mutex wrapping the data
		mutex = Mutex([])

	# Lock the mutex for the scope of the `with` block
		with mutex.lock() as value:
			# value is typed as `list` here
			value.append(1)
		```
	"""

	def __init__(self, value: T):
		# Name it with two underscores to make it a bit harder to accidentally access the value from the outside.
		self.__value = value
		self.__lock = Lock()

	@contextlib.contextmanager
	def lock(self) -> Result[ContextManager[T], RuntimeError]:
		if self.__dropped:
			yield Err(RuntimeError("Mutex has been dropped"))
		self.__lock.acquire()
		try:
			yield Ok(self.__value)
		finally:
			self.__lock.release()

	def __str__(self) -> str:
		return f"Mutex[{self.__value}]"

	def take(self) -> Result[T, RuntimeError]:
		if self.__dropped:
			return Err(RuntimeError("Mutex has been dropped"))
		self.__dropped = True
		return Ok(self.__value)
