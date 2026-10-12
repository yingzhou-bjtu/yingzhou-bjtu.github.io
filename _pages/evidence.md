---
layout: default
title: "Awards & Coverage | 周瀛 (Ying Zhou)"
permalink: /evidence/
description: "周瀛（Ying Zhou）的奖项、专利、IETF Internet-Draft、机构报道和公开履历链接。"
author_profile: true
type: article
---

# Awards & Coverage

## Awards & Campus Records

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

## Patents

{% for item in site.data.evidence.patents %}
### {{ item.title }}

- 公开号：`{{ item.publication_number }}`
- 状态：{{ item.status }}
- 日期：{{ item.date }}
- 发明人位次：{{ item.inventor_order }}
- 申请人：{{ item.assignee }}
- [Google Patents]({{ item.url }})

{% endfor %}

## Internet-Drafts

{% for item in site.data.evidence.internet_drafts %}
### {{ item.title }}

- 文档名：`{{ item.name }}`
- 作者位次：{{ item.author_order }}
- 状态：{{ item.status }}
- [IETF Datatracker]({{ item.url }})

{% endfor %}

## University & Institutional Coverage

{% for item in site.data.evidence.institutional_news %}
- **{{ item.date }}**：[{{ item.title }}]({{ item.url }})，{{ item.publisher }}
{% endfor %}

## Media & Community Coverage

{% for item in site.data.evidence.media_coverage %}
### {{ item.title }}

- 平台：{{ item.publisher }}
- 日期：{{ item.date }}
- 相关身份：{{ item.role }}
- 说明：{{ item.detail }}
- [Article search record]({{ item.url }})

{% endfor %}

## Profiles

- [ORCID 0009-0001-9803-262X]({{ site.data.evidence.identity.orcid }})
- [IEEE Xplore Author 37087009843]({{ site.data.evidence.identity.ieee_author }})
- [GitHub: yingzhou-bjtu]({{ site.data.evidence.identity.github }})
- [IETF Datatracker: Ying Zhou]({{ site.data.evidence.identity.ietf }})
