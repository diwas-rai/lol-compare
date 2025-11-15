#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";
import { CdkStack } from "../lib/cdk-stack";
import { CertificateStack } from "../lib/certificate-stack";
import { FrontendStack } from "../lib/frontend-stack";

const domainName = "lol-compare.co.uk"
const siteSubDomain = "www"

const app = new cdk.App();
new CdkStack(app, "CdkStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});

const certificateStack = new CertificateStack(app, "CertificateStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: "us-east-1",
  },
  domainName,
  siteSubDomain,
  crossRegionReferences: true,
});

new FrontendStack(app, "FrontendStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  domainName,
  siteSubDomain,
  certificate: certificateStack.certificate,
  crossRegionReferences: true,
});
