export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export PUBLIC_ECR_ADDRESS=public.ecr.aws/v3o4w1g6
export PRIVATE_ECR_ADDRESS="${ACCOUNT_ID}".dkr.ecr."${AWS_DEFAULT_REGION}".amazonaws.com
export REPOSITORY=aws-codeseeder/code-build-base
export VERSION=$(cat ${DIR}/VERSION)
