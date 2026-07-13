from typing import Optional, Union

class ViewDescriptor:
    def __init__(self, name: str, select_query: str):
        self.name = name
        self.select_query = select_query

class ViewDependencyGraph:
    def __init__(self):
        self.dependencies: dict[str, list[str]] = {}

    def add_dependency(self, view_name: str, depends_on: str) -> None:
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
                self._dependency_graph.add_dependency(view_name, dep)
                
        self.views[schema_name][view_name] = view
        return view

    def drop_view(self, schema_name: str, view_name: str) -> None:
        if schema_name in self.views and view_name in self.views[schema_name]:
            del self.views[schema_name][view_name]

    def get_view(self, schema_name: str, view_name: str) -> View:
        if schema_name not in self.views or view_name not in self.views[schema_name]:
            raise ValueError(f"View {view_name} not found in schema {schema_name}")
        return self.views[schema_name][view_name]
