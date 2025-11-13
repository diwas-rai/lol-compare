import * as cdk from "aws-cdk-lib";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";

export class CdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const imageTag = new cdk.CfnParameter(this, "imageTag", {
      type: "String",
      description: "The Docker image tag from the CI pipeline.",
      default: "latest",
    });

    const backendRepo = ecr.Repository.fromRepositoryName(
      this,
      "BackendRepo",
      "lol-compare/backend"
    );

    const dockerFunc = new lambda.DockerImageFunction(this, "DockerFunc", {
      code: lambda.DockerImageCode.fromEcr(backendRepo, {
        tag: imageTag.valueAsString,
      }),

      memorySize: 3008,
      timeout: cdk.Duration.seconds(10),
      architecture: lambda.Architecture.ARM_64,
      environment: {
        "NUMBA_CACHE_DIR": "/tmp",
        "JOBLIB_TEMP_FOLDER": "/tmp"
      }
    });

    const functionUrl = dockerFunc.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedMethods: [lambda.HttpMethod.GET, lambda.HttpMethod.POST],
        allowedHeaders: ["Content-Type"],
        allowedOrigins: ["*"],
      },
    });

    new cdk.CfnOutput(this, "FunctionUrlValue", {
      value: functionUrl.url,
    });
  }
}