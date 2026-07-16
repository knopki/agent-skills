# region MODULE_CONTRACT
# PURPOSE: [Describe the GOAL of the module — what business/operational need it fulfills, why.]
# SCOPE:
# - [Main functional areas covered by the module.]
# - NOT: [What is out of scope]
# INVARIANTS: [Condition/State that always holds]
# USECASES:
# - [Entity]: [Actor] => [Action] => [Goal]
# DEPENDENCIES: [Non-trivial deps - USES API: ..., READS: ..., WRITES: ...]
# RATIONALE:
# - Q: [Why was it implemented this way?]
#   A: [Justification, environmental constraints.]
# KEYWORDS: [Comma-separated keywords for grep search]
# endregion MODULE_CONTRACT

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# region VARIABLE_optional_input
# PURPOSE: [Describe the GOAL of this variable and why.]
variable "example_input" {
  description = "Optional human-facing description."
  type        = string
  default     = null
}
# endregion VARIABLE_optional_input

# region RESOURCE_example_bucket
# PURPOSE: [Goal of the resource and why — what it enables the user/agent to do.]
resource "aws_s3_bucket" "example" {
  bucket = var.example_input

  # trivial nested block — markup not needed
  tags = {
    ManagedBy = "terraform"
  }

  # region BLOCK_lifecycle_rules Non-trivial lifecycle rules block summary
  # ... skip 10 lines
  lifecycle_rule {
    id      = "transition-to-ia"
    enabled = true

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
  }
  # ... skip 10 lines
  # endregion BLOCK_lifecycle_rules
}
# endregion RESOURCE_example_bucket

# region LOCALS_common_tags
# PURPOSE: [Describe the GOAL of these locals and why.]
locals {
  common_tags = {
    Environment = "production"
    Project     = "example"
  }
}
# endregion LOCALS_common_tags

# region OUTPUT_example_arn
# PURPOSE: [Describe the GOAL of this output and why.]
output "example_arn" {
  description = "Optional human-facing description."
  value       = aws_s3_bucket.example.arn
}
# endregion OUTPUT_example_arn
