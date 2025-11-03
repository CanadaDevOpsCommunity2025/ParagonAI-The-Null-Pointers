"""
Docker Service - Build Docker images from generated files
"""

import tempfile
import asyncio
import os
from typing import Dict
from pathlib import Path


class DockerService:
    """Service for building Docker images"""
    
    async def build_image(
        self,
        generated_files: Dict[str, str],
        image_tag: str,
        deployment_id: str
    ) -> str:
        """
        Build Docker image from generated files
        
        Args:
            generated_files: Dict of file paths and content
            image_tag: Docker image tag
            deployment_id: Deployment ID for context
        
        Returns:
            Image tag
        """
        # Create temporary build context
        with tempfile.TemporaryDirectory() as build_dir:
            build_path = Path(build_dir)
            
            # Write all files to build context
            for file_path, content in generated_files.items():
                file_full_path = build_path / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content)
            
            # Build Docker image
            process = await asyncio.create_subprocess_exec(
                'docker', 'build',
                '-t', image_tag,
                str(build_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode()
                raise Exception(f"Docker build failed: {error_msg}")
            
            print(f"✅ Docker image built: {image_tag}")
            return image_tag
    
    async def tag_image(self, source_tag: str, target_tag: str):
        """Tag a Docker image"""
        process = await asyncio.create_subprocess_exec(
            'docker', 'tag', source_tag, target_tag,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            raise Exception("Failed to tag Docker image")

