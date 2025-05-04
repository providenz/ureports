import math
import json
from collections import defaultdict
import copy

OFFSET_STEP = 0.001


def group_markers_by_coordinates_and_activity(markers):
    unique_markers = {}

    for marker in markers:
        key = (marker.location.x, marker.location.y, marker.category.name)
        unique_markers[
            key
        ] = marker  # Этот шаг гарантирует, что маркеры с одинаковыми координатами и активностью будут уникальными
    return list(unique_markers.values())


def adjust_markers_based_on_count(unique_markers):
    adjusted_markers = []
    num_markers = len(unique_markers)
    for idx, marker in enumerate(unique_markers):
        new_marker = copy.deepcopy(marker)

        # Вычислите угол для текущего маркера на основе его индекса и количества маркеров
        angle = 2 * math.pi * idx / num_markers

        # Определите радиус для маркера
        radius = OFFSET_STEP * num_markers * 2 / math.pi

        # Вычислите новые координаты на основе угла и радиуса
        new_x = marker.location.x + radius * math.cos(angle)
        new_y = marker.location.y + radius * math.sin(angle)

        new_marker.location.x = new_x
        new_marker.location.y = new_y

        adjusted_markers.append(new_marker)
    return adjusted_markers
