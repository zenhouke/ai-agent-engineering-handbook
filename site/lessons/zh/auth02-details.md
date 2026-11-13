## 本节应交付的设计产物

PEP/PDP位置、缓存失效键、不可用处理、委派范围与审计关联。

代码实现的是应用会话与受控草稿准备：认证主体由可信入口注入，不含OIDC、Cookie或登录凭据签发。策略是局部RBAC+ABAC示例，不假装部署了OPA/Cedar/OpenFGA。所有成员关系变化递增全局policy epoch，保守地使旧审批失效；生产可按策略/资源事实做更细粒度版本。

审批只被原子消费为本地pending操作，没有执行网络写入。执行worker在新副作用前仍须复核撤销/权限，已有UNKNOWN先查原回执。会话失效不抹除业务任务或已经产生的外部效果。

依据：[OPA Policy Language](https://www.openpolicyagent.org/docs/policy-language), [OpenFGA Authorization Concepts](https://openfga.dev/docs/authorization-concepts).
