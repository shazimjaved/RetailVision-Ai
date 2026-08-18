import pytest
import numpy as np
from src.movement_heatmap import MovementHeatmap

def test_initialization():
    heatmap = MovementHeatmap(100, 100)
    assert heatmap.width == 100
    assert heatmap.height == 100
    assert heatmap.density_matrix.shape == (100, 100)
    assert np.all(heatmap.density_matrix == 0)

def test_add_point_within_bounds():
    heatmap = MovementHeatmap(100, 100)
    heatmap.add_point(50, 50, weight=1.0, radius=5)
    
    # Check that density increased at the center
    assert heatmap.density_matrix[50, 50] == 1.0
    
    # Check that density increased at the edge of radius
    assert heatmap.density_matrix[50+5, 50] == 1.0
    
    # Check that outside radius is still 0
    assert heatmap.density_matrix[50+6, 50] == 0.0

def test_add_point_out_of_bounds():
    heatmap = MovementHeatmap(100, 100)
    heatmap.add_point(150, 150)
    # Shouldn't crash and should remain empty
    assert np.all(heatmap.density_matrix == 0)

def test_accumulation():
    heatmap = MovementHeatmap(100, 100)
    heatmap.add_point(50, 50, weight=1.0, radius=2)
    heatmap.add_point(50, 50, weight=2.0, radius=2)
    
    assert heatmap.density_matrix[50, 50] == 3.0
    
    peak_loc, peak_val = heatmap.get_peak_density()
    assert peak_val == 3.0
    # Peak loc could be any within the circle, but usually (50, 50) is found first
    assert peak_loc[0] in range(48, 53)
    assert peak_loc[1] in range(48, 53)

def test_generate_heatmap_empty():
    heatmap = MovementHeatmap(100, 100)
    bg = np.zeros((100, 100, 3), dtype=np.uint8)
    
    result = heatmap.generate_heatmap(bg)
    assert result.shape == (100, 100, 3)
    # An empty heatmap overlaid on black bg should remain black
    assert np.all(result == 0)

def test_generate_heatmap_normalization():
    heatmap = MovementHeatmap(100, 100)
    heatmap.add_point(50, 50, weight=100.0, radius=10)
    bg = np.zeros((100, 100, 3), dtype=np.uint8)
    
    result = heatmap.generate_heatmap(bg, blur_radius=5)
    
    # The max value should trigger red/white colors from COLORMAP_HOT
    # It shouldn't crash, and shouldn't just be black
    assert np.any(result > 0)
    
def test_bg_resizing():
    heatmap = MovementHeatmap(100, 100)
    bg = np.zeros((50, 50, 3), dtype=np.uint8) # Wrong size
    
    # The method should automatically resize bg to match heatmap
    result = heatmap.generate_heatmap(bg)
    assert result.shape == (100, 100, 3)
