import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TerraformService:
    def __init__(self):
        self.terraform_bin = "terraform"
    
    def init(self, working_dir: str) -> bool:
        """Initialize Terraform working directory"""
        try:
            result = subprocess.run(
                [self.terraform_bin, "init"],
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"Terraform initialized in {working_dir}")
                return True
            else:
                logger.error(f"Terraform init failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error initializing Terraform: {e}")
            return False
    
    def plan(self, working_dir: str, var_file: Optional[str] = None) -> bool:
        """Run Terraform plan"""
        try:
            cmd = [self.terraform_bin, "plan"]
            if var_file:
                cmd.extend(["-var-file", var_file])
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Terraform plan successful")
                logger.debug(result.stdout)
                return True
            else:
                logger.error(f"Terraform plan failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error running Terraform plan: {e}")
            return False
    
    def apply(self, working_dir: str, var_file: Optional[str] = None, auto_approve: bool = False) -> bool:
        """Apply Terraform configuration"""
        try:
            cmd = [self.terraform_bin, "apply"]
            if var_file:
                cmd.extend(["-var-file", var_file])
            if auto_approve:
                cmd.append("-auto-approve")
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Terraform apply successful")
                return True
            else:
                logger.error(f"Terraform apply failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error applying Terraform: {e}")
            return False
    
    def destroy(self, working_dir: str, var_file: Optional[str] = None, auto_approve: bool = False) -> bool:
        """Destroy Terraform-managed infrastructure"""
        try:
            cmd = [self.terraform_bin, "destroy"]
            if var_file:
                cmd.extend(["-var-file", var_file])
            if auto_approve:
                cmd.append("-auto-approve")
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Terraform destroy successful")
                return True
            else:
                logger.error(f"Terraform destroy failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error destroying Terraform resources: {e}")
            return False
    
    def output(self, working_dir: str, output_name: Optional[str] = None) -> Optional[str]:
        """Get Terraform output values"""
        try:
            cmd = [self.terraform_bin, "output", "-json"]
            if output_name:
                cmd.append(output_name)
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Terraform output failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Error getting Terraform output: {e}")
            return None


terraform_service = TerraformService()