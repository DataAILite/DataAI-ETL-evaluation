Class DataAI.ETL.Status Extends %RegisteredObject
{

ClassMethod About() As %String
{
    Return "DataAI ETL IRIS bootstrap module. Spark libraries are licensed and delivered separately."
}

ClassMethod SuggestedSchema() As %String
{
    Return "DataAI"
}

}
