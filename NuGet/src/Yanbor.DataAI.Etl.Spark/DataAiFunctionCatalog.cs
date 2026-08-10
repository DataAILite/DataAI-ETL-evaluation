namespace Yanbor.DataAI.Etl.Spark;

public sealed record DataAiFunctionDescriptor(string Family, string Capability, string JavaApi);

/// <summary>Catalog of the computational functions included in the runtime package.</summary>
public static class DataAiFunctionCatalog
{
    public static IReadOnlyList<DataAiFunctionDescriptor> All { get; } =
    [
        new("ETL and quality", "Normalize fields", "DataAiPipeline.normalize"),
        new("ETL and quality", "Deterministic record key", "DataAiPipeline.recordKey"),
        new("ETL and quality", "Field profiling", "FieldProfiler.profile"),
        new("ETL and quality", "Declarative validation", "DataAiPipeline.validate"),
        new("ETL and quality", "Automatic quality checks", "DataQualityFunctions.automaticChecks"),
        new("ETL and quality", "Missing-value summary", "DataQualityFunctions.missingValueSummary"),
        new("ETL and quality", "Duplicate-record summary", "DataQualityFunctions.duplicateRecordSummary"),
        new("ETL and quality", "Invalid-date summary", "DataQualityFunctions.invalidDateSummary"),
        new("ETL and quality", "Numeric-outlier summary", "DataQualityFunctions.numericOutlierSummary"),
        new("ETL and quality", "Category consistency", "DataQualityFunctions.inconsistentCategorySummary"),
        new("ETL and quality", "Suspicious text", "DataQualityFunctions.suspiciousTextSummary"),
        new("Analytics", "Grouped descriptive statistics", "AnalyticsFunctions.groupedSummary"),
        new("Analytics", "Pivot and cross-tab", "AnalyticsFunctions.pivot"),
        new("Analytics", "Variance and contribution", "AnalyticsFunctions.variance"),
        new("Analytics", "Ranking", "AnalyticsFunctions.ranking"),
        new("Analytics", "Pairwise correlation", "AnalyticsFunctions.correlations"),
        new("Analytics", "Correlation threshold", "AnalyticsFunctions.correlationThreshold"),
        new("Analytics", "Linear regression and prediction", "AnalyticsFunctions.linearRegression"),
        new("Time analysis", "Period summary", "TimeSeriesFunctions.summarize"),
        new("Time analysis", "Moving average and rolling total", "TimeSeriesFunctions.rolling"),
        new("Business", "Outliers", "BusinessFunctions.outliers"),
        new("Business", "Anomaly scores", "BusinessFunctions.anomalyScores"),
        new("Business", "Distribution drift", "BusinessFunctions.drift"),
        new("Business", "ABC and Pareto classification", "BusinessFunctions.pareto"),
        new("Business", "Cohort retention", "BusinessFunctions.cohort"),
        new("Business", "Funnel conversion", "BusinessFunctions.funnel"),
        new("Business", "KPI calculations", "BusinessFunctions.kpi"),
        new("Market", "Demand", "MarketFunctions.demand"),
        new("Market", "Price sensitivity", "MarketFunctions.pricing"),
        new("Market", "Elasticity", "MarketFunctions.elasticity"),
        new("Market", "Basket analysis", "MarketFunctions.basket"),
        new("Market", "Segments", "MarketFunctions.segments"),
        new("Market", "Churn and retention", "MarketFunctions.churn"),
        new("Market", "Risk", "MarketFunctions.risk"),
        new("Market", "Inventory", "MarketFunctions.inventory"),
        new("Market", "Profit and margin", "MarketFunctions.profit"),
        new("Market", "Scenario analysis", "MarketFunctions.scenario"),
        new("Geographic", "Map readiness", "MapFunctions.readiness"),
        new("Matrix", "Matrix balancing", "MatrixFunctions.balance"),
        new("Insights", "Data dictionary", "InsightFunctions.dataDictionary"),
        new("Insights", "Chart recommendations", "InsightFunctions.chartRecommendations"),
        new("Insights", "Deterministic narratives", "InsightFunctions.narratives"),
        new("Insights", "Rule-based alerts", "InsightFunctions.ruleBasedAlerts")
    ];
}
