import requests
import networkx as nx
import constants

pub_listing_url = "https://www.designsafe-ci.org/api/publications/v2"


def get_ds_pubs():
    """Return a generator of top-level publication metadata"""
    offset = 0
    limit = 100
    res_length = 100
    while res_length == 100:
        res = requests.get(pub_listing_url, params={"offset": offset, "limit": limit})
        res_json = res.json()

        yield from res_json["result"]
        res_length = len(res_json["result"])
        offset += 100


def get_publication(project_id: str):
    """Retrieve published metadata using the project ID."""
    res = requests.get(f"{pub_listing_url}/{project_id}")
    return res.json()


def iterate_publications():
    """Generator of all published metadata"""
    for pub in get_ds_pubs():
        if pub["type"] not in ["other", "field_reconnaissance"]:
            yield get_publication(pub["projectId"])


DISPLAY_NAMES = {
    constants.PROJECT: "Project",
    # Experimental
    constants.EXPERIMENT: "Experiment",
    constants.EXPERIMENT_MODEL_CONFIG: "Model Configuration",
    constants.EXPERIMENT_SENSOR: "Sensor Information",
    constants.EXPERIMENT_ANALYSIS: "Analysis",
    constants.EXPERIMENT_EVENT: "Event",
    constants.EXPERIMENT_REPORT: "Report",
    # Simulation
    constants.SIMULATION: "Simulation",
    constants.SIMULATION_MODEL: "Simulation Model",
    constants.SIMULATION_INPUT: "Simulation Input",
    constants.SIMULATION_OUTPUT: "Simulation Output",
    constants.SIMULATION_ANALYSIS: "Analysis",
    constants.SIMULATION_REPORT: "Report",
    # Hybrid sim
    constants.HYBRID_SIM: "Hybrid Simulation",
    constants.HYBRID_SIM_REPORT: "Report",
    constants.HYBRID_SIM_ANALYSIS: "Analysis",
    constants.HYBRID_SIM_GLOBAL_MODEL: "Global Model",
    constants.HYBRID_SIM_COORDINATOR: "Master Simulation Coordinator",
    constants.HYBRID_SIM_SIM_SUBSTRUCTURE: "Simulation Substructure",
    constants.HYBRID_SIM_EXP_SUBSTRUCTURE: "Experimental Substructure",
    constants.HYBRID_SIM_EXP_OUTPUT: "Experimental Output",
    constants.HYBRID_SIM_COORDINATOR_OUTPUT: "Coordinator Output",
    constants.HYBRID_SIM_SIM_OUTPUT: "Simulation Output",
    # Field Recon
    constants.FIELD_RECON_MISSION: "Mission",
    constants.FIELD_RECON_COLLECTION: "Collection",
    constants.FIELD_RECON_GEOSCIENCE: "Geoscience Collection",
    constants.FIELD_RECON_SOCIAL_SCIENCE: "Social Science Collection",
    constants.FIELD_RECON_REPORT: "Document Collection",
    constants.FIELD_RECON_PLANNING: "Research Planning Collection",
}

file_ext_descriptors = {
    "ipynb": "Jupyter Notebook",
    "txt": "text file",
    "py": "python script",
    "png": "PNG image",
    "pdf": "PDF file",
    "csv": "CSV file",
}


def get_pub_vectors(pub_meta: dict) -> list[str]:
    """Walk the entity tree and return a list of natural-language descriptors."""
    pub_graph = nx.tree_graph(pub_meta["tree"])

    pub_vectors = []

    shortest_paths = nx.single_source_all_shortest_paths(pub_graph, "NODE_ROOT")

    for node, path in shortest_paths:
        node_value = pub_graph.nodes[node]["value"]
        description = node_value.get("description", "")
        authors = node_value.get("authors", [])
        file_objs = node_value.get("fileObjs", [])
        file_tags = node_value.get("fileTags", [])

        context_comps = []

        for path_node in path[0]:
            node_value = pub_graph.nodes[path_node]["value"]
            node_name = pub_graph.nodes[path_node]["name"]

            node_display = DISPLAY_NAMES[node_name]
            context_comps.append(f"{node_display}: {node_value.get('title', '')}")

        context_comps = context_comps[::-1]

        if description:
            desc_format = f"description: {description}"

            pub_vectors.append(
                ", in ".join(
                    [
                        desc_format,
                        *context_comps,
                    ]
                )
            )

        if authors:
            for author in authors:
                pub_vectors.append(
                    ", in ".join(
                        [f"author: {author['fname']} {author['lname']}", *context_comps]
                    )
                )

        if file_objs:
            for file_obj in file_objs:

                if file_obj["type"] == "dir":
                    fo_type = "directory/folder"
                else:
                    fo_ext = file_obj["name"].split(".", 1)[-1]
                    fo_type = file_ext_descriptors.get(fo_ext, "file")
                fo_format = (
                    f"{fo_type} with name {file_obj['name']} at path {file_obj['path']}"
                )
                tags = [
                    t["tagName"] for t in file_tags if t["path"] == file_obj["path"]
                ]
                if tags:
                    tag_format = f"{','.join(tags)}"
                    fo_format += f", tags: {tag_format}"
                pub_vectors.append(
                    ", in ".join(
                        [
                            fo_format,
                            *context_comps,
                        ]
                    )
                )

    return [v.replace("\n", " ") for v in pub_vectors]
