import os
import subprocess

def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise Exception(f"Command failed with exit code {e.returncode}: {e.stderr.strip()}") from e

# Set variables
cluster_name = os.environ.get("CLUSTER_NAME") 
account_id = run_command("aws sts get-caller-identity --query 'Account' --output text")     
region = os.environ.get("AWS_REGION")              
policy_name = f"AWSLoadBalancerControllerIAMPolicy-{cluster_name}"
role_name = f"AmazonEKSLoadBalancerControllerRole-{cluster_name}"
lb_controller_image = os.environ.get("LB_CONTROLLER_IMAGE") 

# Step 1: Check if IAM Policy exists
def policy_exists():
    print("Checking if IAM policy exists...")
    cmd = f"aws iam list-policies --query 'Policies[?PolicyName==`{policy_name}`].PolicyName' --output text"
    result = run_command(cmd)
    exists = result == policy_name
    if exists:
        print("IAM policy already exists.")
    return exists

def create_iam_policy():
    if policy_exists():
        return
    print("Creating IAM policy...")
    iam_policy_url = "https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json"
    policy_file = "iam_policy.json"
    
    subprocess.run(["curl", "-O", iam_policy_url], check=True)
    
    create_policy_cmd = [
        "aws", "iam", "create-policy",
        "--policy-name", policy_name,
        "--policy-document", f"file://{policy_file}"
    ]
    
    subprocess.run(create_policy_cmd, check=True)
    os.remove(policy_file)
    print("IAM policy created successfully.")

# Step 2: Check if IAM Role exists
def create_iam_role():
    print("Creating IAM role and service account...")

    # Check if the service account exists
    check_sa_cmd = (
        f"kubectl get serviceaccount aws-load-balancer-controller-{cluster_name} "
        f"--namespace=kube-system"
    )

    try:
        run_command(check_sa_cmd)
        print("Service account already exists.")
    except Exception as e:
        print("Service account does not exist. Creating it with the existing IAM role...")

        # Command to create the IAM service account using the existing role
        create_iam_sa_cmd = (
            f"eksctl create iamserviceaccount "
            f"--cluster={cluster_name} "
            f"--namespace=kube-system "
            f"--name=aws-load-balancer-controller-{cluster_name} "
            f"--role-name={role_name} "
            f"--attach-policy-arn=arn:aws:iam::{account_id}:policy/{policy_name} "
            f"--approve"
        )

        run_command(create_iam_sa_cmd)
        print("IAM role and service account created successfully.")

# Step 3: Install AWS Load Balancer Controller using Helm
def install_lb_controller():
    print("Installing AWS Load Balancer Controller...")

    helm_command = (
        f"helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller "
        f"--namespace kube-system "
        f"--version 1.5.5 "
        f"--set clusterName={cluster_name} "
        f"--set serviceAccount.create=false "
        f"--set serviceAccount.name=aws-load-balancer-controller-{cluster_name} "
        f"--set image.repository={lb_controller_image} " 
        f"--set image.tag=aws-alb-controller-v2.5.4 "  # This line will ensure the private ECR image is used
        f"--set region={region} "
        f"--set awsVpcID=vpc-00be237934c6972a4 " 
        f"--wait"
    )

    run_command(helm_command)
    
    print("AWS Load Balancer Controller installed successfully.")

# Step 4: Verify Installation
def verify_installation():
    print("Verifying AWS Load Balancer Controller installation...")
    verify_cmd = ["kubectl", "get", "deployment", "aws-load-balancer-controller", "-n", "kube-system"]
    subprocess.run(verify_cmd, check=True)

# Main function to execute the steps
if __name__ == "__main__":
    create_iam_policy()
    create_iam_role()
    install_lb_controller()
    verify_installation()
    print("AWS Load Balancer Controller setup completed successfully.")
