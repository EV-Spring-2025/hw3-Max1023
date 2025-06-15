import cv2
import numpy as np
import math
import argparse
import sys

def calculate_psnr(original_frame, compressed_frame):
    """
    Calculates the PSNR between two video frames.

    Args:
        original_frame (np.ndarray): The original, uncompressed frame.
        compressed_frame (np.ndarray): The compressed frame.

    Returns:
        float: The PSNR value. Returns float('inf') if frames are identical.
    """
    # Convert frames to float type for calculation
    original_frame = original_frame.astype(np.float64)
    compressed_frame = compressed_frame.astype(np.float64)

    # Calculate Mean Squared Error (MSE)
    mse = np.mean((original_frame - compressed_frame) ** 2)

    # If MSE is zero, the frames are identical, so PSNR is infinite.
    if mse == 0:
        return float('inf')

    # Maximum possible pixel value (for 8-bit color depth)
    max_pixel = 255.0

    # Calculate PSNR using the formula: 20 * log10(MAX / sqrt(MSE))
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    
    return psnr

def main():
    """
    Main function to process videos and calculate average PSNR.
    """
    # --- 1. Set up Argument Parser ---
    # This makes the script easy to use from the command line.
    parser = argparse.ArgumentParser(description="Calculate the PSNR between two video files.")
    parser.add_argument("original_video", help="Path to the original (reference) video file.")
    parser.add_argument("compressed_video", help="Path to the compressed (distorted) video file.")

    args = parser.parse_args()

    # --- 2. Open Video Files ---
    original_cap = cv2.VideoCapture(args.original_video)
    compressed_cap = cv2.VideoCapture(args.compressed_video)

    # Check if videos opened successfully
    if not original_cap.isOpened():
        print(f"Error: Could not open original video file: {args.original_video}")
        sys.exit(1)
    if not compressed_cap.isOpened():
        print(f"Error: Could not open compressed video file: {args.compressed_video}")
        sys.exit(1)

    # --- 3. Verify Video Properties ---
    # For a valid comparison, videos should have the same dimensions and frame count.
    original_frame_count = int(original_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    compressed_frame_count = int(compressed_cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if original_frame_count != compressed_frame_count:
        print("Warning: Videos have different frame counts.")
        print(f"Original: {original_frame_count} frames, Compressed: {compressed_frame_count} frames.")
        print("PSNR will be calculated for the shorter video's duration.")

    original_width = int(original_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(original_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    compressed_width = int(compressed_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    compressed_height = int(compressed_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if original_width != compressed_width or original_height != compressed_height:
        print("Error: Video dimensions do not match.")
        print(f"Original: {original_width}x{original_height}, Compressed: {compressed_width}x{compressed_height}")
        sys.exit(1)


    # --- 4. Process Frames and Calculate PSNR ---
    total_psnr = 0
    frame_number = 0

    while True:
        # Read one frame from each video
        ret_orig, frame_orig = original_cap.read()
        ret_comp, frame_comp = compressed_cap.read()

        # If either video ends, break the loop
        if not ret_orig or not ret_comp:
            break

        # Calculate PSNR for the current pair of frames
        psnr = calculate_psnr(frame_orig, frame_comp)
        
        if psnr != float('inf'):
            total_psnr += psnr
        
        frame_number += 1
        print(f"Processing Frame {frame_number}/{min(original_frame_count, compressed_frame_count)} - PSNR: {psnr:.2f} dB")

    # --- 5. Calculate and Display Average PSNR ---
    if frame_number > 0:
        average_psnr = total_psnr / frame_number
        print("\n---------------------------------")
        print(f"Average PSNR: {average_psnr:.2f} dB")
        print("---------------------------------")
    else:
        print("Error: No frames were processed.")

    # --- 6. Release Resources ---
    original_cap.release()
    compressed_cap.release()

if __name__ == '__main__':
    main()
