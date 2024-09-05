# AWS Load Balancer Controller Setup

This project automates the setup and installation of the AWS Load Balancer Controller(chart version 1.5.5) on an EKS cluster using a Python script and a GitHub Actions workflow.

## Prerequisites

- An EKS cluster is already set up and accessible.
- You have configured a GitHub Actions runner, preferably self-hosted, to execute the workflow.
- AWS CLI is installed on the GitHub Actions runner.
- Role with GitHub repo trust relationships. You can refer to role/github-access-policies and role/trust-relationships code(don't forget to update placeholders).

## Python Script

The lb-controller-python-script.py script performs the following tasks:

1. IAM Policy Creation: Checks if an IAM policy for the AWS Load Balancer Controller already exists. If not, it creates one.
2. IAM Role and Service Account Creation: Checks if the necessary IAM role and Kubernetes service account exist. If they don't, it creates them.
3. CRD Application: Applies the required Custom Resource Definitions (CRDs) for the AWS Load Balancer Controller.
4. AWS Load Balancer Controller Installation: Installs the AWS Load Balancer Controller using a Helm chart from the repository and updates the container image in the generated YAML file.
5. Installation Verification: Verifies that the AWS Load Balancer Controller is installed correctly by checking the deployment status.

## GitHub Actions Workflow

The GitHub Actions workflow, Install AWS Load Balancer Controller, automates the process of running the Python script on your EKS cluster.

### Workflow Details

1. Trigger: The workflow is triggered manually via the workflow_dispatch event
2. Runner: The workflow runs on a self-hosted GitHub Actions runner labeled prod-runner.
3. Environment Variables: The workflow uses environment variables defined in GitHub Secrets and Variables.
4. Timeout: The job has a timeout of 15 minutes.

## Updating GitHub Secrets and Variables

To successfully run this workflow, you need to configure the following secrets and variables in your GitHub repository:

1. Secrets

- lb_controller_Role: The ARN of the IAM role to assume when running the workflow.

2. Variables

- CLUSTER_NAME: The name of your EKS cluster.
- AWS_REGION: The AWS region where your EKS cluster is located.
- LB_CONTROLLER_IMAGE: The Docker image for the AWS Load Balancer Controller, stored in Amazon ECR.

## How to Run the Workflow

1. Navigate to the GitHub repository.
2. Go to the Actions tab.
3. Select the Install AWS Load Balancer Controller workflow.
4. Click the Run workflow button and enter the script name (default: lb-controller-python-script.py).
5. Click Run workflow.

## Verify lb-controller Installation

1. Run the following command to verify the installation:

```
kubectl get deploy -n kube-system
kubectl get pods -n kube-system
```

## Set up Ingress and verify

1. Update the ingress.yaml file and run the following command to set up ingress:

```
kubectl apply -f ingress.yaml
kubectl get ingress
```

2. You should see the external address associated with the Ingress controller listed in the output.

### Note

1. If you want to install the latest version of AWS Load Balancer Controller, follow these steps:

2. Install the latest AWS Load Balancer Controller Helm chart on your local system and replace the aws-load-balancer-controller directory in your repository with the latest one.
   Update the version in the iam_policy_url within the lb-controller-python-script.py file.

3. Run the workflow.

## Conclusion

This setup allows you to quickly and reliably deploy the AWS Load Balancer Controller to your EKS cluster using a combination of Python scripting and GitHub Actions. Make sure to keep your GitHub secrets and variables updated to ensure the workflow runs smoothly.
