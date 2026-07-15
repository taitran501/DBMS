from typing import Optional, Union

class ViewDescriptor:
    def __init__(self, name: str, select_query: str):
        self.name = name
        self.select_query = select_query

class ViewDependencyGraph:
    def __init__(self):
        self.dependencies: dict[str, list[str]] = {}

    def add_view_dependency(self, view_name: str, depends_on: str) -> None:
        if view_name not in self.dependencies:
            self.dependencies[view_name] = []
        self.dependencies[view_name].append(depends_on)

class View:
    def __init__(self, name: Union[str, ViewDescriptor], select_query: Optional[str] = None):
        if isinstance(name, ViewDescriptor):
            self.descriptor = name
            self.name = name.name
            self.select_query = name.select_query
        else:
            self.descriptor = ViewDescriptor(name, select_query or "")
            self.name = name
            self.select_query = select_query or ""

class ViewManager:
    def __init__(self, dependency_graph: Optional[ViewDependencyGraph] = None):
        self._dependency_graph = dependency_graph or ViewDependencyGraph()
        # schema_name -> dict of views (view_name -> View)
        self.views: dict[str, dict[str, View]] = {}

    @staticmethod
    def _view_key(schema_name: str, view_name: str) -> str:
        """Keep legacy bare names while isolating views in canonical schemas."""
        return f"{schema_name}.{view_name}" if "." in schema_name else view_name

    def create_view(self, schema_name: str, view_name: str, select_query: str, depends_on: Optional[list[str]] = None) -> View:
        if schema_name not in self.views:
            self.views[schema_name] = {}
        if view_name in self.views[schema_name]:
            raise ValueError(f"View {view_name} already exists in schema {schema_name}")
        
        # Build ViewDescriptor
        descriptor = ViewDescriptor(view_name, select_query)
        view = View(descriptor)
        
        # Track dependencies
        if depends_on:
            for dep in depends_on:
                self._dependency_graph.add_view_dependency(self._view_key(schema_name, view_name), dep)
                
        self.views[schema_name][view_name] = view
        return view

    def drop_view(self, schema_name: str, view_name: str) -> None:
        if schema_name in self.views and view_name in self.views[schema_name]:
            del self.views[schema_name][view_name]
            self._dependency_graph.dependencies.pop(self._view_key(schema_name, view_name), None)

    def rename_dependency(self, old_dependency: str, new_dependency: str) -> None:
        for view_name, dependencies in self._dependency_graph.dependencies.items():
            self._dependency_graph.dependencies[view_name] = [new_dependency if dependency == old_dependency else dependency for dependency in dependencies]

    def rename_database_scope(self, database_name: str, new_name: str) -> None:
        old_prefix, new_prefix = f"{database_name}.", f"{new_name}."
        for schema_name in tuple(self.views):
            if schema_name.startswith(old_prefix):
                self.views[f"{new_prefix}{schema_name[len(old_prefix):]}"] = self.views.pop(schema_name)
        renamed_dependencies = {}
        for view_name, dependencies in self._dependency_graph.dependencies.items():
            renamed_view_name = f"{new_prefix}{view_name[len(old_prefix):]}" if view_name.startswith(old_prefix) else view_name
            renamed_dependencies[renamed_view_name] = [dependency.replace(old_prefix, new_prefix, 1) if old_prefix in dependency else dependency for dependency in dependencies]
        self._dependency_graph.dependencies = renamed_dependencies

    def get_view(self, schema_name: str, view_name: str) -> View:
        if schema_name not in self.views or view_name not in self.views[schema_name]:
            raise ValueError(f"View {view_name} not found in schema {schema_name}")
        return self.views[schema_name][view_name]
