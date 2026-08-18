import cv2
import numpy as np

class MovementHeatmap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Float32 array to accumulate density without rapid overflow
        self.density_matrix = np.zeros((height, width), dtype=np.float32)
        self.max_density_ever = 1.0 # To keep normalization stable over time if desired
        
    def add_point(self, x: int, y: int, weight: float = 1.0, radius: int = 15):
        """
        Add a point to the density matrix. 
        We draw a small circle to give the point initial spatial volume.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            # Draw a solid circle on a temporary mask, then add to density matrix
            # Doing this efficiently:
            y_min = max(0, y - radius)
            y_max = min(self.height, y + radius + 1)
            x_min = max(0, x - radius)
            x_max = min(self.width, x + radius + 1)
            
            # Create a meshgrid for the localized patch
            Y, X = np.ogrid[y_min:y_max, x_min:x_max]
            dist_sq = (X - x)**2 + (Y - y)**2
            mask = dist_sq <= radius**2
            
            self.density_matrix[y_min:y_max, x_min:x_max][mask] += weight

    def get_peak_density(self):
        """Returns the (x, y) location and value of the highest density spot."""
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(self.density_matrix)
        return max_loc, float(max_val)

    def generate_heatmap(self, bg_image: np.ndarray, blur_radius: int = 61, alpha_factor: float = 0.6) -> np.ndarray:
        """
        Generates the heatmap overlay on the background image.
        """
        # 1. Apply Gaussian smoothing
        # Ensure blur_radius is odd
        if blur_radius % 2 == 0:
            blur_radius += 1
            
        smoothed = cv2.GaussianBlur(self.density_matrix, (blur_radius, blur_radius), 0)
        
        # 2. Normalize to 0-255
        max_val = np.max(smoothed)
        if max_val > 0:
            normalized = (smoothed / max_val * 255).astype(np.uint8)
        else:
            normalized = np.zeros_like(smoothed, dtype=np.uint8)
            
        # 3. Apply COLORMAP_HOT
        heatmap_color = cv2.applyColorMap(normalized, cv2.COLORMAP_HOT)
        
        # 4. Blend using the normalized heat as an alpha channel
        # This makes low-heat areas transparent (black in COLORMAP_HOT becomes fully transparent)
        # We can apply a curve or threshold to the alpha if we want to drop very low noise
        
        alpha_mask = (normalized.astype(np.float32) / 255.0) * alpha_factor
        # Expand dims to multiply with 3-channel images
        alpha_mask = np.expand_dims(alpha_mask, axis=2)
        
        # Ensure bg_image matches dimensions
        if bg_image.shape[:2] != (self.height, self.width):
            bg_image = cv2.resize(bg_image, (self.width, self.height))
            
        # Blend
        blended = (heatmap_color * alpha_mask + bg_image * (1.0 - alpha_mask)).astype(np.uint8)
        
        return blended
