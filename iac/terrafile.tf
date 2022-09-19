provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "maria-quiteria-tfstate1"
    key    = "iac/terraform.tfstate"
    region = "us-east-1"
  }
}

data "template_file" "container_definitions" {
  template = file("./container_definitions.json")
  vars = {
    IMAGE = var.image
  }
}

module "ecs_mentoria" {
  source                = "git::https://github.com/mentoriaiac/iac-modulo-aws-ecs.git?ref=ebfe0d63e4afa387b390cc91f44e12c89ba3bdea"
  create_cluster        = true
  app_count             = 1
  fargate_cpu           = 256
  fargate_memory        = 512
  subnet_ids            = ["subnet-07e64bae35c703e59", "subnet-076661f11f71e2c7e"]
  vpc_id                = "vpc-0ca967f989c37ad90"
  protocol              = "HTTP"
  family_name           = "mentoria"
  service_name          = "mentoria"
  cluster_name          = "mentoria"
  container1_name       = "api"
  container1_port       = 8000
  container_definitions = data.template_file.container_definitions.rendered
  depends_on            = ["module.rds_mariaquiteria"]

  tags = {
    Env          = "production"
    Team         = "tematico-terraform"
    System       = "api-tika"
    CreationWith = "terraform"
    Repository   = "https://github.com/mentoriaiac/iac-modulo-aws-ecs"
  }
}

output "load_balancer_dns_name" {
  value = "http://${module.ecs_mentoria.loadbalance_dns_name}"
}

output "security_group_id" {
  value = module.ecs_mentoria.security_group_id
}

variable "image" {
  type        = string
  description = "Nome da Imagem"
}

terraform {
  required_version = ">= 1.0.0"

}

module "rds_mariaquiteria" {
  source                  = "git::https://github.com/mentoriaiac/iac-modulo-aws-rds.git"
  subnet_ids              = ["subnet-07e64bae35c703e59", "subnet-076661f11f71e2c7e"]
  proj_name               = "mariaquiteria"
  vpc_id                  = "vpc-0ca967f989c37ad90"
  port                    = 5432
  storage                 = 20
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "12.7"
  instance_type           = "db.t2.micro"
  db_name                 = "mariaquiteria"
  db_username             = "postgres"
  identifier              = "mariaquiteria"
  parameter_group_name    = "default.postgres12"
  snapshot                = true
  publicly_accessible_rds = true
  default_tags = {
    Name        = "RDS_mariaquiteria",
    Team        = "Mentoria-IAC",
    Application = "maria-quiteria",
    Environment = "Production",
    Terraform   = "Yes",
    Owner       = "Mentoria-IAC"
  }
  parameters = [{
    name        = "sentry_dsn",
    description = "Parâmetro referente à variável de ambiente SENTRY_DSN",
    type        = "String",
    value       = " "
    },
    {
      name        = "spidermon_telegram_fake",
      description = "Parâmetro referente à variável de ambiente SPIDERMON_TELEGRAM_FAKE"
      type        = "String"
      value       = " "
    },
    {
      name        = "spidermon_sentry_fake",
      description = "Parâmetro referente à variável de ambiente SPIDERMON_SENTRY_FAKE"
      type        = "String"
      value       = " "
    },
    {
      name        = "django_settings_module",
      description = "Parâmetro referente à variável de ambiente DJANGO_SETTINGS_MODULE"
      type        = "String"
      value       = " "

    },
    {
      name        = "django_configuration",
      description = "Parâmetro referente à variável de ambiente DJANGO_CONFIGURATION"
      type        = "String"
      value       = " "
    },
    {
      name        = "django_secret_key",
      description = "Parâmetro referente à variável de ambiente DJANGO_SECRET_KEY"
      type        = "String"
      value       = " "
    },
    {
      name        = "access_token_lifetime_in_minutes",
      description = "Parâmetro referente à variável de ambiente ACCESS_TOKEN_LIFETIME_IN_MINUTES"
      type        = "String"
      value       = " "
    },
    {
      name        = "refresh_token_lifetime_in_minutes",
      description = "Parâmetro referente à variável de ambiente REFRESH_TOKEN_LIFETIME_IN_MINUTES"
      type        = "String"
      value       = " "

    },
    {
      name        = "aws_s3_bucket",
      description = "Parâmetro referente à variável de ambiente AWS_S3_BUCKET"
      type        = "String"
      value       = "maria-quiteria-tfstate1"
    },
    {
      name        = "aws_s3_bucket_folder",
      description = "Parâmetro referente à variável de ambiente AWS_S3_BUCKET_FOLDER"
      type        = "String"
      value       = " "
    },
    {
      name        = "aws_s3_region",
      description = "Parâmetro referente à variável de ambiente AWS_S3_REGION"
      type        = "String"
      value       = "us-east-1"
  }]
}
