import * as cdk from "aws-cdk-lib";
import * as acm from "aws-cdk-lib/aws-certificatemanager";
import * as route53 from "aws-cdk-lib/aws-route53";
import { Construct } from "constructs";

interface CertificateStackProps extends cdk.StackProps {
  domainName: string;
  siteSubDomain: string;
}

export class CertificateStack extends cdk.Stack {
  public readonly certificate: acm.ICertificate;
  
  constructor(scope: Construct, id: string, props: CertificateStackProps) {
    super(scope, id, props);

    const { domainName, siteSubDomain } = props;
    const siteDomain = `${siteSubDomain}.${domainName}`;

    const zone = route53.HostedZone.fromLookup(this, "Zone", { domainName });

    const certificate = new acm.Certificate(this, "SiteCertificate", {
      domainName: siteDomain,
      validation: acm.CertificateValidation.fromDns(zone),
    });

    this.certificate = certificate;
  }
}
