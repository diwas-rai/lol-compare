import * as cdk from "aws-cdk-lib";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as cloudfront from "aws-cdk-lib/aws-cloudfront";
import * as origins from "aws-cdk-lib/aws-cloudfront-origins";
import * as route53 from "aws-cdk-lib/aws-route53";
import { CloudFrontTarget } from "aws-cdk-lib/aws-route53-targets";
import * as s3 from "aws-cdk-lib/aws-s3";
import * as s3deploy from "aws-cdk-lib/aws-s3-deployment";
import { Construct } from "constructs";

interface FrontendStackProps extends cdk.StackProps {
  domainName: string;
  siteSubDomain: string;
  certificate: acm.ICertificate;
  apiUrl: string;
}

export class FrontendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props);

    const { domainName, siteSubDomain, certificate } = props;
    const siteDomain = `${siteSubDomain}.${domainName}`;

    const siteBucket = new s3.Bucket(this, "SiteBucket", {
      bucketName: siteDomain,
      publicReadAccess: false,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const zone = route53.HostedZone.fromLookup(this, "Zone", { domainName });

    const distribution = new cloudfront.Distribution(this, "Distribution", {
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(siteBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      certificate: certificate,
      domainNames: [siteDomain],
      sslSupportMethod: cloudfront.SSLMethod.SNI,
      defaultRootObject: "index.html",
    });

    new route53.ARecord(this, "SiteAliasRecord", {
      recordName: siteDomain,
      target: route53.RecordTarget.fromAlias(
        new CloudFrontTarget(distribution)
      ),
      zone,
    });

    new s3deploy.BucketDeployment(this, "DeployWithInvalidation", {
      sources: [s3deploy.Source.asset("../frontend/dist"),
        s3deploy.Source.data(
        "config.js",
        `window.VITE_APP_API_URL="${props.apiUrl}";` 
        )
      ],
      destinationBucket: siteBucket,
      distribution,
      distributionPaths: ["/*"],
    });

    new cdk.CfnOutput(this, "SiteURL", { value: `https://${siteDomain}` });
  }
}
