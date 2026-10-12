---
layout: default
title: "Verified Record｜周瀛（Ying Zhou）"
permalink: /evidence/
description: "周瀛（Ying Zhou）的可核验公开记录，包括奖项、专利、IETF Internet-Draft、机构新闻和学术身份链接。"
author_profile: true
type: article
---

# Verified Record

本页只收录能够回到公开来源的记录。奖项、论文、专利和标准草案分别标注状态，避免把申请公开写成授权、把 Internet-Draft 写成 IETF 标准。

最后核验日期：**{{ site.data.evidence.verified_on }}**。

## 奖项与校级记录

{% for item in site.data.evidence.awards %}
### {{ item.title }}

- 时间：{{ item.year }}
- 角色：{{ item.role }}
- 说明：{{ item.detail }}

来源：
{% for source in item.sources %}
- [{{ source.label }}]({{ source.url }})
{% endfor %}

{% endfor %}

## 专利

{% for item in site.data.evidence.patents %}
### {{ item.title }}

- 公开号：`{{ item.publication_number }}`
- 状态：{{ item.status }}
- 日期：{{ item.date }}
- 发明人位次：{{ item.inventor_order }}
- 申请人：{{ item.assignee }}
- [Google Patents]({{ item.url }})

{% endfor %}

## IETF Internet-Draft

{% for item in site.data.evidence.internet_drafts %}
### {{ item.title }}

- 文档名：`{{ item.name }}`
- 作者位次：{{ item.author_order }}
- 状态：{{ item.status }}
- [IETF Datatracker]({{ item.url }})

{% endfor %}

## 机构新闻与公开记录

{% for item in site.data.evidence.institutional_news %}
- **{{ item.date }}**：[{{ item.title }}]({{ item.url }})，{{ item.publisher }}
{% endfor %}

## 北京广西博联及媒体报道

{% for item in site.data.evidence.media_coverage %}
### {{ item.title }}

- 平台：{{ item.publisher }}
- 日期：{{ item.date }}
- 相关身份：{{ item.role }}
- 说明：{{ item.detail }}
- [微信公开检索记录]({{ item.url }})

{% endfor %}

## 待补公开来源的个人记录

以下内容由周瀛本人确认，但尚未取得文章原版、证书或正式获奖名单。此处只作为待核验记录保存，不作为已核验事实对外引用。

{% for item in site.data.evidence.pending_public_records %}
- **{{ item.date }}**：{{ item.title }}。{{ item.detail }}
{% if item.url %}
  [相关赛事页面]({{ item.url }})
{% endif %}
{% endfor %}

## 学术身份

- [ORCID 0009-0001-9803-262X]({{ site.data.evidence.identity.orcid }})
- [IEEE Xplore Author 37087009843]({{ site.data.evidence.identity.ieee_author }})
- [GitHub: yingzhou-bjtu]({{ site.data.evidence.identity.github }})
- [IETF Datatracker: Ying Zhou]({{ site.data.evidence.identity.ietf }})
