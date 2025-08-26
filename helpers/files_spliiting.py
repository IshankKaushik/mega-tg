import os
import logging
from filesplit.split import Split

logger = logging.getLogger(__name__)

def split_files(file_path, split_size, output_dir):
    """Split large files into smaller chunks"""
    try:
        split = Split(file_path, output_dir)
        split.bysize(split_size)
        logger.info(f"File split successfully: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error splitting file {file_path}: {e}")
        raise

async def split_video_files(file_path, split_size, output_dir, filename):
    """Split video files using ffmpeg for better quality"""
    try:
        import asyncio
        import math
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Calculate number of parts
        num_parts = math.ceil(file_size / split_size)
        
        # Get video duration
        duration_cmd = [
            "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", file_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *duration_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        try:
            total_duration = float(stdout.decode().strip())
        except (ValueError, AttributeError):
            logger.warning("Could not get video duration, falling back to file splitting")
            return split_files(file_path, split_size, output_dir)
        
        # Calculate segment duration
        segment_duration = total_duration / num_parts
        
        # Split video using ffmpeg
        for i in range(num_parts):
            start_time = i * segment_duration
            output_file = os.path.join(output_dir, f"{filename}_part_{i+1:03d}.mp4")
            
            split_cmd = [
                "ffmpeg", "-i", file_path,
                "-ss", str(start_time),
                "-t", str(segment_duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_file, "-y"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *split_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            
            if not os.path.exists(output_file):
                logger.error(f"Failed to create video segment: {output_file}")
                # Fallback to file splitting
                return split_files(file_path, split_size, output_dir)
        
        logger.info(f"Video split successfully into {num_parts} parts")
        return True
        
    except Exception as e:
        logger.error(f"Error splitting video {file_path}: {e}")
        # Fallback to regular file splitting
        return split_files(file_path, split_size, output_dir)
