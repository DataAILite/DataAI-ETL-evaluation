package com.dataai.etl.spark.functions;

import java.util.List;

public final class DataAiFunctionCatalog {
    private DataAiFunctionCatalog() {
    }

    public static List<Entry> entries() {
        return List.of(
                new Entry("Profiling", "FieldProfiler.profile", "Quality", "Counts, distinct values, range, average, and standard deviation"),
                new Entry("Normalization", "DataAiPipeline.normalize", "ETL", "Snake-case names, trimmed strings, and blank-to-null conversion"),
                new Entry("Declarative quality rules", "DataAiPipeline.validate", "Quality", "Required, unique, range, set, date, length, equality, and regex rules"),
                new Entry("Automatic quality", "DataQualityFunctions.automaticChecks", "Quality", "Missing, duplicates, invalid dates, numeric outliers, category variants, and suspicious text"),
                new Entry("Grouped statistics", "AnalyticsFunctions.groupedSummary", "Analytics", "Count, distinct count, sum, min, max, average, and standard deviation"),
                new Entry("Pivot / cross-tab", "AnalyticsFunctions.pivot", "Analytics", "Row and column grouped matrix output"),
                new Entry("Variance / comparison", "AnalyticsFunctions.variance", "Analytics", "Base, comparison, variance, percent change, and contribution"),
                new Entry("Ranking", "AnalyticsFunctions.ranking", "Analytics", "Top, bottom, and average-nearest ranking"),
                new Entry("Correlation", "AnalyticsFunctions.correlations", "Analytics", "Pairwise correlation, direction, strength, and thresholds"),
                new Entry("Regression", "AnalyticsFunctions.linearRegression", "Analytics", "Linear equation, correlation, R-squared, and prediction"),
                new Entry("Time summaries", "TimeSeriesFunctions.summarize", "Time", "Day, week, month, quarter, and year summaries"),
                new Entry("Rolling time series", "TimeSeriesFunctions.rolling", "Time", "Moving average, rolling total, and period change"),
                new Entry("Outlier flagging", "BusinessFunctions.outliers", "Analytics", "Standard deviation, percent difference, and business range"),
                new Entry("Anomaly scoring", "BusinessFunctions.anomalyScores", "Analytics", "Transparent within-group anomaly score"),
                new Entry("Data drift", "BusinessFunctions.drift", "Quality", "Base versus comparison distribution drift points"),
                new Entry("ABC Pareto", "BusinessFunctions.pareto", "Business", "Contribution, cumulative share, and ABC class"),
                new Entry("Cohort", "BusinessFunctions.cohort", "Business", "First-activity cohorts and retention"),
                new Entry("Funnel", "BusinessFunctions.funnel", "Business", "Stage conversion and drop-off"),
                new Entry("KPI", "BusinessFunctions.kpi", "Business", "Ratio, difference, sum, and product KPIs"),
                new Entry("Market demand", "MarketFunctions.demand", "Market", "Demand share and assumption projection"),
                new Entry("Market pricing", "MarketFunctions.pricing", "Market", "Price bands, quantity, revenue, and sensitivity"),
                new Entry("Market elasticity", "MarketFunctions.elasticity", "Market", "Price/quantity elasticity and revenue projection"),
                new Entry("Market basket", "MarketFunctions.basket", "Market", "Transaction co-occurrence and support"),
                new Entry("Market segments", "MarketFunctions.segments", "Market", "Segment value and average comparison"),
                new Entry("Market churn", "MarketFunctions.churn", "Market", "Recency retention score and churn status"),
                new Entry("Market risk", "MarketFunctions.risk", "Market", "Relative exposure score"),
                new Entry("Market inventory", "MarketFunctions.inventory", "Market", "Velocity, supply periods, and reorder point"),
                new Entry("Market profit", "MarketFunctions.profit", "Market", "Cost, profit, margin, and contribution"),
                new Entry("Market scenario", "MarketFunctions.scenario", "Market", "Downside, base, and upside values"),
                new Entry("Map readiness", "MapFunctions.readiness", "Geographic", "Missing, invalid, duplicate, and KML-ready coordinates"),
                new Entry("Matrix balancing", "MatrixFunctions.balance", "Matrix", "Iterative row and column target balancing"),
                new Entry("Data dictionary", "InsightFunctions.dataDictionary", "Insight", "Detected roles and suggested uses"),
                new Entry("Chart recommendations", "InsightFunctions.chartRecommendations", "Insight", "Schema-based chart choices and priorities"),
                new Entry("Automated narratives", "InsightFunctions.narratives", "Insight", "Deterministic local explanations without an external service"),
                new Entry("Rule-based alerts", "InsightFunctions.ruleBasedAlerts", "Insight", "Quality alerts and recommended next function"));
    }

    public record Entry(String capability, String api, String category, String description) {
    }
}
