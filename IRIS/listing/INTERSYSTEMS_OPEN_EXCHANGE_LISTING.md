# InterSystems Open Exchange Listing

## Recommended listing

- **Name:** DataAI ETL for InterSystems IRIS
- **Publisher:** Yanbor LLC, provider of the DataAI product
- **Category:** Analytics (use Interoperability if requested by review)
- **Technologies:** InterSystems IRIS; IRIS for Health only after direct testing;
  HealthShare only after direct testing
- **Industries:** Healthcare, financial services, government, manufacturing,
  and general services as applicable
- **Tags:** ETL, data quality, Apache Spark, analytics, JDBC, matrix balancing,
  AI, governance
- **AI/ML:** Select only to describe DataAI analytical functionality; do not
  imply an external generative-AI service

## Short description

Run DataAI's complete Spark ETL, data-quality, analytical, market, geographic,
matrix-balancing, and insight libraries against customer-controlled
InterSystems IRIS data through JDBC—without a hosted DataAI service.

## Full description

DataAI ETL for InterSystems IRIS embeds DataAI computation inside the
customer's Apache Spark application. Teams can read governed IRIS SQL tables,
normalize and validate records, profile fields, route clean and rejected rows,
run business and market analytics, evaluate geographic readiness, balance
matrices, and explicitly persist approved outputs to IRIS.

The adapter uses Spark's standard JDBC integration and does not bundle the
InterSystems JDBC driver. The customer selects a driver compatible with its
IRIS and Java versions and controls credentials, namespaces, SQL schemas,
partitioning, save modes, scheduling, security, retention, and monitoring.

The evaluation package contains only fictional data. DataAI does not require a
hosted service, telemetry, call-home licensing, or customer-data transmission.

## Call to action

- Button: **Request DataAI IRIS Evaluation**
- URL: `[DATAAI IRIS EVALUATION URL]`

Do not link directly to an anonymous production JAR. Evaluation fulfillment
should issue customer-specific, expiring private Maven credentials.

## Required public URLs

- About: `[DATAAI IRIS PRODUCT URL]`
- License: `[PUBLIC DATAAI LICENSE URL]`
- Documentation: `[PUBLIC DATAAI IRIS DOCUMENTATION URL]`
- Support: `[DATAAI SUPPORT URL]`
- Demo: `[DATAAI IRIS DEMO URL]`
- Privacy: `[DATAAI PRIVACY URL]`
- Terms: `[DATAAI TERMS URL]`

## Licensing

The optional demonstration/IPM bootstrap is free. DataAI Spark evaluation is
limited by `LICENSE.md` to less than 32 consecutive calendar days. Production,
continued use, redistribution, OEM, or managed-service use requires written
commercial terms. Software is provided **AS IS**, with no obligations except
those expressly accepted in a signed commercial agreement or order form.

## Submission checklist

1. Replace every bracketed URL.
2. Test the exact supported IRIS, IRIS JDBC driver, Java 17, Spark 3.5, and
   Scala 2.12 combinations.
3. Test IRIS for Health/HealthShare before selecting them.
4. Run the full Maven reactor and offline package validator.
5. Validate JDBC reads, partitioning, writes, retry behavior, types, and
   least-privilege identities.
6. Verify all examples and screenshots use fictional data.
7. Publish public documentation and a support intake process.
8. Create an Open Exchange account and choose **New Application**.
9. Complete name, logo, category, technologies, industries, CTA, license,
   tags, descriptions, documentation, support, demo, version, and release
   notes.
10. Save, preview, and select **Send for Approval**.
11. Address review recommendations and retest the final listing download path.
12. Publish the IPM bootstrap only after separate IPM testing.

## Monetization boundary

Open Exchange is the discovery channel. DataAI contracts and collects payment
directly, executes the commercial agreement/order form, and delivers immutable
production artifacts through an authenticated Maven repository. The public IPM
module and marketplace page must not bypass commercial entitlement.
