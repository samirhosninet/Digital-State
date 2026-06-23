# قالب تسليم الدولة الرقمية
# Digital State Handoff Protocol Template — Arabic/English

> تنسيق موحّد لجميع التسليمات بين الوكلاء في الدولة الرقمية.

## تنسيق التسليم / Handoff Format

```text
[من: <وكيل>] [إلى: <وكيل>] [بطاقة: <رقم>]
[FROM: <agent>] [TO: <agent>] [CARD: <card_id>]
إجراء / Action: <فعل / VERB>
ملخص / Summary: <ما تم / ما المطلوب>
أدلة / Evidence: <سجلات خام، مصادر، مخرجات أوامر — أو N/A>
معايير القبول / Acceptance Criteria: <قائمة — أو N/A>
حدود الملف / File Boundaries: <مسارات دقيقة — أو N/A>
شرط التوقف / Stop Condition: <متى يتوقف>
```

## أزواج المصدر-الهدف الصالحة / Valid Source-Target Pairs

| من / FROM | إلى / TO | إجراءات صالحة / Valid Actions |
|-----------|----------|-------------------------------|
| builder | prime | COMPLETE, BLOCK |
| auditor | prime | APPROVE, APPROVE WITH WARNINGS, REJECT, ESCALATE |
| prime | builder | EVIDENCE, IMPLEMENT |
| prime | auditor | AUDIT |

## تسليم البناء → الرئيسي / Builder → Prime Handoff

```text
[FROM: builder] [TO: prime] [CARD: t_xxxxxxxx]
Action: BLOCK
Summary: review-required: <ملخص الأدلة في سطر واحد>
Evidence: <أرفق مخرجات التنفيذ، نتائج الاختبار، تغييرات الملفات>
File Boundaries: <المسارات المعدّلة بالضبط>
Stop Condition: صدور APPROVE أو APPROVE WITH WARNINGS من المراجع
```

> **ملاحظة مهمة**: يجب على البناء استخدام `kanban_block(reason="review-required: ...")` — وليس `kanban_complete()` — لبطاقات التنفيذ التي تحتاج مراجعة. الرئيسي يرقّي نفس البطاقة إلى `status='review'` (المادة الرابعة عشرة من الدستور).
