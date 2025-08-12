# Samsung Feedback AI - End-to-End Workflow

```mermaid
flowchart TD
    Start[Start] --> DataCollection
    DataCollection --> DataProcessing
    DataProcessing --> Analysis
    Analysis --> Solutions
    Solutions --> Dashboard

    subgraph DataCollection
        DC1[Fetch PlayStore Reviews]
        DC2[Scrape Social Media]
        DC3[Import External Data]
        DC4[Store Raw Data in DB]
    end

    subgraph DataProcessing
        DP1[Clean & Preprocess Text]
        DP2[Rule-based Classification]
        DP3[Zero-shot Classification]
        DP4[Store Classified Data]
    end

    subgraph Analysis
        A1[Generate Sentence Embeddings]
        A2[KMeans Clustering]
        A3[Extract Keywords per Cluster]
        A4[Create Problem Summaries]
    end

    subgraph Solutions
        S1[Generate AI Recommendations]
        S2[Create Action Plans]
        S3[Prioritize Solutions]
        S4[Generate Executive Summary]
    end

    subgraph Dashboard
        DB1[Load Processed Data]
        DB2[Interactive Visualizations]
        DB3[Problem Cluster Explorer]
        DB4[Solution Recommendations]
        DB5[Export Reports]
    end

    Dashboard --> End[End]
