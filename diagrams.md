# Diagrams

```mermaid
graph TD;
    analyze_endpoint["/issues/{issue_number}/analyze (POST)"] -->|Depends| configure_repository
    analyze_endpoint -->|Depends| configure_unit_of_work
    configure_repository -->|Returns| repo["RepositoryProtocol[Issue]"]
    configure_unit_of_work -->|Returns| uow["UnitOfWorkProtocol[ConnectionProtocol]"]
    analyze_endpoint --> ApplicationFacade_analyze_issue["ApplicationFacade.analyze_issue()"]
    ApplicationFacade_analyze_issue --> AnalyzeIssue_constructor["AnalyzeIssue.__init__()"]
    AnalyzeIssue_constructor --> AnalyzeIssue_analyze["AnalyzeIssue.analyze()"]
    AnalyzeIssue_analyze --> repo_get_by_id["repo.get_by_id()"]
    repo_get_by_id -->|Issue found| AnalyzeIssue_analyze
    repo_get_by_id -->|Issue not found| repo_add["repo.add()"]

    repo_add --> AnalyzeIssue_analyze
```

```mermaid
graph TD;
    analyze_endpoint["/issues/{issue_number}/analyze (POST)"] -->|Depends| configure_repository["configure_repository()"]
    analyze_endpoint -->|Depends| configure_unit_of_work["configure_unit_of_work()"]
    configure_repository -->|Returns| repo["RepositoryProtocol[Issue]"]
    configure_unit_of_work -->|Returns| uow["UnitOfWorkProtocol[ConnectionProtocol]"]
    analyze_endpoint --> ApplicationFacade_analyze_issue["ApplicationFacade.analyze_issue()"]
    ApplicationFacade_analyze_issue --> AnalyzeIssue_constructor["AnalyzeIssue.__init__()"]
    AnalyzeIssue_constructor --> AnalyzeIssue_analyze["AnalyzeIssue.analyze()"]
    AnalyzeIssue_analyze --> repo_get_by_id["repo.get_by_id()"]
    repo_get_by_id -->|Issue found| AnalyzeIssue_analyze
    repo_get_by_id -->|Issue not found| repo_add["repo.add()"]
    repo_add --> AnalyzeIssue_analyze
    configure_unit_of_work --> UnitOfWork_constructor["UnitOfWork.__init__()"]
    UnitOfWork_constructor --> UnitOfWork_commit["UnitOfWork.commit()"]
    UnitOfWork_constructor --> UnitOfWork_rollback["UnitOfWork.rollback()"]
    UnitOfWork_constructor --> UnitOfWork_enter["UnitOfWork.__enter__()"]
    UnitOfWork_constructor --> UnitOfWork_exit["UnitOfWork.__exit__()"]
    UnitOfWork_commit --> Connection_commit["Connection.commit()"]
    UnitOfWork_rollback --> Connection_rollback["Connection.rollback()"]
    Connection_commit -.-> ConnectionProtocol
    Connection_rollback -.-> ConnectionProtocol
    UnitOfWork_commit -.-> UnitOfWorkProtocol
    UnitOfWork_rollback -.-> UnitOfWorkProtocol
    UnitOfWork_enter -.-> UnitOfWorkProtocol
    UnitOfWork_exit -.-> UnitOfWorkProtocol
```
