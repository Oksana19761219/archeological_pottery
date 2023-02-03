import pandas as pd
import  numpy as np


def find_closest_node(node, nodes):
    dist = np.sum((nodes - node) ** 2, axis=1)
    closest_node = nodes[np.argmin(dist)]
    nodes = np.delete(nodes, np.argmin(dist), 0)
    return closest_node, nodes


def calculate_curvature(ordered_nodes):
    """
    calculate curve curvature:
    https://stackoverflow.com/questions/28269379/curve-curvature-in-numpy
    """
    dx_dt = np.gradient(ordered_nodes[:, 0])
    dy_dt = np.gradient(ordered_nodes[:, 1])
    d2x_dt2 = np.gradient(dx_dt)
    d2y_dt2 = np.gradient(dy_dt)
    curvature = (d2x_dt2 * dy_dt - dx_dt * d2y_dt2) / (dx_dt * dx_dt + dy_dt * dy_dt) ** 1.5
    return curvature


def order_curve_nodes(nodes):
    nodes_y_max = nodes[nodes['y'] == nodes['y'].max()]
    start_node = nodes_y_max[nodes_y_max['x'] == nodes_y_max['x'].max()]

    nodes = nodes.drop(index=start_node.index)
    nodes = np.asarray(nodes)
    node = np.asarray(start_node)
    ordered_nodes = node

    for item in range(len(nodes)):

        node, nodes = find_closest_node(node, nodes)
        ordered_nodes = np.append(ordered_nodes, node.reshape((1, 2)), axis=0)
    return ordered_nodes

