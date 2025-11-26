#!/usr/bin/env node
import * as cdk from "aws-cdk-lib/core";
import { BackendStack } from "../lib/backend-stack";
import { CertificateStack } from "../lib/certificate-stack";
import { FrontendStack } from "../lib/frontend-stack";

const domainName = "lol-compare.co.uk";
const siteSubDomain = "www";

const app = new cdk.App();
const backendStack = new BackendStack(app, "BackendStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  crossRegionReferences: true,
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
  apiUrl: backendStack.functionUrl.url,
  crossRegionReferences: true,
});
