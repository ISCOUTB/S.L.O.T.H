import proto_utils
import inspect
from types import ModuleType
from typing import Any, Set, Optional


def print_module_tree(
    mod: ModuleType, indent: int = 0, visited: Optional[Set[int]] = None
) -> None:
    if visited is None:
        visited = set()
    if id(mod) in visited:
        return
    visited.add(id(mod))

    prefix = "    " * indent
    for name in dir(mod):
        if name.startswith("_"):
            continue

        attr: Any = getattr(mod, name)

        if (
            inspect.ismodule(attr)
            and getattr(attr, "__package__", None)
            and (attr.__package__ or "").startswith(mod.__package__ or mod.__name__)
        ):
            print(f"{prefix}{name}/")
            print_module_tree(attr, indent + 1, visited)
            continue

        if inspect.isfunction(attr):
            print(f"{prefix}{name}()")
            continue

        if inspect.isclass(attr):
            print(f"{prefix}{name} (class)")


def main():
    print_module_tree(proto_utils)


if __name__ == "__main__":
    main()
