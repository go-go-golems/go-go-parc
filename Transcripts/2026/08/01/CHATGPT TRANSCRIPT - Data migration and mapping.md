# Data migration and mapping

- URL: https://chatgpt.com/c/6a6e0125-5484-83ea-8d57-6a682c7900fc
- Created: 2026-08-01T14:23:17.377Z

---

> So wait, so you have people submitting data. So it's like CSVs or JSON of all their data from their business. We take that and then we, so right now the way they do it, it takes months all manually. What I'm building right now is to basically one shot, attempt to one shot it, or not one shot it, but get it done automatically, and then just have the human review it. So they give us, they have like their members, their billing, their classes, their points, all that, and I'm like taking that, and it comes from, because we have like dozens of competitors, and we have a lot of people come from competitors. Dozens like millions. Oh right, yeah, yeah. But the top, the top ones that we do like are like, you know, just a handful. So we take those structures and I'm trying to like figure out the best way to map it. Yeah, I can share.

What you're describing is a data migration and schema mapping system, not just an ETL pipeline.

The core problem is:

- Input: CSVs


---

> Invent an elegant fluent builder Js api that is a composable grammar for expressing these transformations with opinionated defaults but can be customized by passing lambda . Show some examples (martial arts studio, cross fit gyms, etc…) to our software : class management, billing , crm, etc…
>
> Only examples from simple to more complex, input csv output structure and js code

<details><summary>💭 Thinking</summary>

**Planning migration examples**

I’m designing progressively complex JavaScript migration examples for martial arts, CrossFit, and CRM data, showing CSV inputs, structured outputs, composable transformations, joins, validation, deduplication, and customizable hooks.

**Planned migration examples**

</details>

I’ll present the API entirely through progressively richer migrations, keeping the grammar consistent across members, billing, classes, CRM, and attendance.

## 1. Martial arts studio — basic member import

### Input: `members.csv`

```csv
Member ID,Student Name,Email,Phone,Program,Active
M-100,Ana Torres,ana@example.com,(512) 555-0198,Kids BJJ,yes
M-101,Marcus Lee,marcus@example.com,512.555.0144,Muay Thai,no
```

### Output

```json
{
  "members": [
    {
      "externalId": "M-100",
      "firstName": "Ana",
      "lastName": "Torres",
      "email": "ana@example.com",
      "phone": "+15125550198",
      "status": "active",
      "tags": ["kids-bjj"]
    },
    {
      "externalId": "M-101",
      "firstName": "Marcus",
      "lastName": "Lee",
      "email": "marcus@example.com",
      "phone": "+15125550144",
      "status": "inactive",
      "tags": ["muay-thai"]
    }
  ]
}
```

### JavaScript

```js
import {
  migrate,
  csv,
  preset,
  text
} from "@ourapp/migrate";

export default migrate("Northside Karate")
  .read(csv("members.csv"))
  .as("members")

  .write("members", members => members
    .rows("members")
    .key("Member ID")

    // Splits names and normalizes email, phone, dates, and empty values.
    .use(preset.member({
      name: "Student Name",
      email: "Email",
      phone: "Phone"
    }))

    .field("status")
      .from("Active")
      .map(value =>
        /^(yes|y|true|1)$/i.test(value)
          ? "active"
          : "inactive"
      )

    .field("tags")
      .from("Program")
      .map(program => [text.slug(program)])
  );
```

---

## 2. CrossFit gym — members, subscriptions, and billing

### Input: `clients.csv`

```csv
Client ID,Name,Email,Phone,Plan Code,Start Date,Status,Billing Customer ID,Autopay
C-100,Jamie Rowe,jamie@example.com,6175550101,UNLIMITED,2026-01-15,Active,cus_981,yes
C-101,Sam Patel,sam@example.com,6175550102,THREE_WEEK,2026-02-01,Paused,cus_982,no
```

### Input: `plans.csv`

```csv
Plan Code,Plan Name,Monthly Price,Billing Day
UNLIMITED,Unlimited CrossFit,189.00,1
THREE_WEEK,3 Classes Per Week,139.00,15
```

### Output

```json
{
  "members": [
    {
      "externalId": "C-100",
      "firstName": "Jamie",
      "lastName": "Rowe",
      "email": "jamie@example.com",
      "phone": "+16175550101",
      "status": "active"
    }
  ],
  "memberships": [
    {
      "externalId": "C-100:UNLIMITED",
      "memberId": "member:C-100",
      "name": "Unlimited CrossFit",
      "status": "active",
      "startsOn": "2026-01-15",
      "billing": {
        "cadence": "monthly",
        "amount": 18900,
        "currency": "USD",
        "chargeDay": 1,
        "autopay": true
      }
    }
  ],
  "billing": {
    "customers": [
      {
        "externalId": "cus_981",
        "memberId": "member:C-100",
        "autopayEnabled": true
      }
    ]
  }
}
```

### JavaScript

```js
import {
  migrate,
  csv,
  preset,
  parse
} from "@ourapp/migrate";

const status = value => ({
  active: "active",
  paused: "paused",
  cancelled: "cancelled",
  canceled: "cancelled"
})[value.trim().toLowerCase()] ?? "inactive";

export default migrate("Legacy CrossFit")
  .read(csv("clients.csv"))
  .as("clients")

  .read(csv("plans.csv"))
  .as("plans")

  .write("members", members => members
    .rows("clients")
    .key("Client ID")
    .use(preset.member({
      name: "Name",
      email: "Email",
      phone: "Phone"
    }))
    .field("status")
      .from("Status")
      .map(status)
  )

  .write("memberships", memberships => memberships
    .rows("clients")
    .join("plans")
      .on("Plan Code")
      .as("plan")

    .key(row => `${row["Client ID"]}:${row["Plan Code"]}`)

    .field("memberId")
      .ref("members")
      .by("Client ID")

    .field("name")
      .from("plan.Plan Name")

    .field("status")
      .from("Status")
      .map(status)

    .field("startsOn")
      .from("Start Date")
      .map(parse.date)

    .field("billing")
      .compute(row => ({
        cadence: "monthly",
        amount: parse.money(row["plan.Monthly Price"], "USD").minor,
        currency: "USD",
        chargeDay: parse.integer(row["plan.Billing Day"]),
        autopay: parse.boolean(row.Autopay)
      }))
  )

  .write("billing.customers", customers => customers
    .rows("clients")
    .where(row => Boolean(row["Billing Customer ID"]))
    .key("Billing Customer ID")

    .field("memberId")
      .ref("members")
      .by("Client ID")

    .field("autopayEnabled")
      .from("Autopay")
      .map(parse.boolean)
  );
```

---

## 3. Martial arts school — recurring classes and bookings

### Input: `members.csv`

```csv
Member ID,Student Name,Email
M-100,Ana Torres,ana@example.com
M-101,Marcus Lee,marcus@example.com
```

### Input: `classes.csv`

```csv
Class ID,Name,Instructor,Days,Start Time,Duration Min,Capacity,Start Date,End Date,Timezone
CL-1,BJJ Fundamentals,Coach Kim,Mon|Wed,18:00,60,20,2026-09-01,2026-12-31,America/New_York
CL-2,Muay Thai,Coach Evans,Tue|Thu,19:30,75,18,2026-09-01,2026-12-31,America/New_York
```

### Input: `bookings.csv`

```csv
Booking ID,Class ID,Member ID,Date,Status
B-900,CL-1,M-100,2026-09-02,Booked
B-901,CL-2,M-101,2026-09-03,Waitlist
```

### Output

```json
{
  "classSeries": [
    {
      "externalId": "CL-1",
      "name": "BJJ Fundamentals",
      "instructorName": "Coach Kim",
      "capacity": 20,
      "recurrence": {
        "weekdays": ["monday", "wednesday"],
        "localStartTime": "18:00",
        "durationMinutes": 60,
        "startsOn": "2026-09-01",
        "endsOn": "2026-12-31",
        "timezone": "America/New_York"
      }
    }
  ],
  "classBookings": [
    {
      "externalId": "B-900",
      "memberId": "member:M-100",
      "classSeriesId": "classSeries:CL-1",
      "startsAt": "2026-09-02T18:00:00-04:00",
      "status": "booked"
    }
  ]
}
```

### JavaScript

```js
import {
  migrate,
  csv,
  preset,
  parse
} from "@ourapp/migrate";

const bookingStatus = value => ({
  booked: "booked",
  confirmed: "booked",
  waitlist: "waitlisted",
  waitlisted: "waitlisted",
  cancelled: "cancelled",
  canceled: "cancelled"
})[value.trim().toLowerCase()] ?? "booked";

export default migrate("Eastside Martial Arts")
  .read(csv("members.csv"))
  .as("members")

  .read(csv("classes.csv"))
  .as("classes")

  .read(csv("bookings.csv"))
  .as("bookings")

  .write("members", members => members
    .rows("members")
    .key("Member ID")
    .use(preset.member({
      name: "Student Name",
      email: "Email"
    }))
  )

  .write("classSeries", classes => classes
    .rows("classes")
    .key("Class ID")

    .field("name")
      .from("Name")

    .field("instructorName")
      .from("Instructor")

    .field("capacity")
      .from("Capacity")
      .map(parse.integer)

    .field("recurrence")
      .compute(row => ({
        weekdays: row.Days
          .split("|")
          .map(parse.weekday),

        localStartTime: parse.time(row["Start Time"]),
        durationMinutes: parse.integer(row["Duration Min"]),
        startsOn: parse.date(row["Start Date"]),
        endsOn: parse.date(row["End Date"]),
        timezone: row.Timezone || "America/New_York"
      }))
  )

  .write("classBookings", bookings => bookings
    .rows("bookings")
    .key("Booking ID")

    .field("memberId")
      .ref("members")
      .by("Member ID")

    .field("classSeriesId")
      .ref("classSeries")
      .by("Class ID")

    .field("startsAt")
      .compute((row, ctx) => {
        const classRow = ctx.lookup(
          "classes",
          "Class ID",
          row["Class ID"]
        );

        return parse.zonedDateTime({
          date: row.Date,
          time: classRow["Start Time"],
          timezone: classRow.Timezone || "America/New_York"
        });
      })

    .field("status")
      .from("Status")
      .map(bookingStatus)

    .review.when(
      (row, ctx) => !ctx.canRef(
        "members",
        "Member ID",
        row["Member ID"]
      ),
      row => `Member ${row["Member ID"]} was not found`
    )
  );
```

---

## 4. Gym CRM — deduplicate leads and preserve notes

### Input: `prospects.csv`

```csv
Lead ID,Full Name,Email,Mobile,Source,Stage,Created At
L-9,Jordan Miles,JORDAN@example.com,617-555-0120,Facebook,Trial Scheduled,2026-07-01 09:30
L-10,Jordan Miles,,(617) 555-0120,Walk In,New,2026-07-02 14:10
L-11,Taylor Wong,taylor@example.com,617-555-0140,Referral,Contacted,2026-07-03 11:00
```

### Input: `notes.csv`

```csv
Note ID,Lead ID,Occurred At,Note
N-1,L-9,2026-07-01 10:00,Interested in the six week challenge
N-2,L-10,2026-07-02 14:15,Came in and toured the gym
N-3,L-11,2026-07-03 12:00,Requested an evening call
```

### Output

```json
{
  "crm": {
    "contacts": [
      {
        "externalId": "jordan@example.com",
        "sourceIds": ["L-9", "L-10"],
        "firstName": "Jordan",
        "lastName": "Miles",
        "email": "jordan@example.com",
        "phone": "+16175550120",
        "leadSources": ["facebook", "walk-in"],
        "createdAt": "2026-07-01T09:30:00-04:00"
      }
    ],
    "opportunities": [
      {
        "externalId": "opportunity:jordan@example.com",
        "contactId": "crmContact:jordan@example.com",
        "pipeline": "membership-sales",
        "stage": "trial-scheduled"
      }
    ],
    "activities": [
      {
        "externalId": "N-1",
        "contactId": "crmContact:jordan@example.com",
        "type": "note",
        "occurredAt": "2026-07-01T10:00:00-04:00",
        "body": "Interested in the six week challenge"
      },
      {
        "externalId": "N-2",
        "contactId": "crmContact:jordan@example.com",
        "type": "note",
        "occurredAt": "2026-07-02T14:15:00-04:00",
        "body": "Came in and toured the gym"
      }
    ]
  }
}
```

### JavaScript

```js
import {
  migrate,
  csv,
  preset,
  normalize,
  parse,
  text
} from "@ourapp/migrate";

const identity = row =>
  normalize.email(row.Email) ||
  normalize.phone(row.Mobile, "US") ||
  `lead:${row["Lead ID"]}`;

const stagePriority = {
  new: 1,
  contacted: 2,
  "trial-scheduled": 3,
  "trial-completed": 4,
  won: 5,
  lost: 5
};

const normalizeStage = value =>
  text.slug(value || "new");

export default migrate("Gym CRM")
  .read(csv("prospects.csv"))
  .as("prospects")

  .read(csv("notes.csv"))
  .as("notes")

  .write("crm.contacts", contacts => contacts
    .rows("prospects")

    .dedupe
      .by(identity)
      .merge((current, incoming) => ({
        ...current,

        Email: current.Email || incoming.Email,
        Mobile: current.Mobile || incoming.Mobile,

        "Created At":
          current["Created At"] < incoming["Created At"]
            ? current["Created At"]
            : incoming["Created At"],

        __leadIds: [
          ...(current.__leadIds || [current["Lead ID"]]),
          incoming["Lead ID"]
        ],

        __sources: [
          ...(current.__sources || [current.Source]),
          incoming.Source
        ]
      }))

    .key(identity)

    // Allows references using any merged legacy Lead ID.
    .aliases(row =>
      row.__leadIds || [row["Lead ID"]]
    )

    .use(preset.contact({
      name: "Full Name",
      email: "Email",
      phone: "Mobile"
    }))

    .field("sourceIds")
      .compute(row =>
        row.__leadIds || [row["Lead ID"]]
      )

    .field("leadSources")
      .compute(row =>
        [...new Set(
          (row.__sources || [row.Source])
            .filter(Boolean)
            .map(text.slug)
        )]
      )

    .field("createdAt")
      .from("Created At")
      .map(value =>
        parse.zonedDateTime(value, "America/New_York")
      )
  )

  .write("crm.opportunities", opportunities => opportunities
    .rows("prospects")

    .dedupe
      .by(identity)
      .merge((current, incoming) => {
        const currentStage = normalizeStage(current.Stage);
        const incomingStage = normalizeStage(incoming.Stage);

        return stagePriority[incomingStage] >
          stagePriority[currentStage]
          ? incoming
          : current;
      })

    .key(row => `opportunity:${identity(row)}`)

    .field("contactId")
      .ref("crm.contacts")
      .by(identity)

    .field("pipeline")
      .value("membership-sales")

    .field("stage")
      .from("Stage")
      .map(normalizeStage)
  )

  .write("crm.activities", activities => activities
    .rows("notes")
    .key("Note ID")

    .field("contactId")
      .ref("crm.contacts")
      .by("Lead ID")

    .field("type")
      .value("note")

    .field("occurredAt")
      .from("Occurred At")
      .map(value =>
        parse.zonedDateTime(value, "America/New_York")
      )

    .field("body")
      .from("Note")
  );
```

---

## 5. Full martial arts academy — households, billing, attendance, ranks, and review

### Input: `students.csv`

```csv
Student ID,Household Code,Student Name,DOB,Email,Phone,Program,Guardian ID
S-1,FAM-22,Mia Chen,2014-05-12,mia.family@example.com,2125550100,Kids BJJ,G-8
S-2,FAM-22,Leo Chen,2011-11-03,mia.family@example.com,2125550100,Teen BJJ,G-8
S-3,FAM-40,Noah Smith,1994-08-20,noah@example.com,6465550199,Muay Thai,
```

### Input: `guardians.csv`

```csv
Guardian ID,Household Code,Name,Email,Phone
G-8,FAM-22,Li Chen,li.chen@example.com,2125550100
```

### Input: `contracts.csv`

```csv
Contract ID,Student ID,Plan,Start Date,End Date,Amount,Cadence,Autopay
CT-1,S-1,Kids Unlimited,2026-01-01,,149.00,Monthly,yes
CT-2,S-2,Teen Unlimited,2026-01-01,,159.00,Monthly,yes
CT-3,S-3,Muay Thai Unlimited,2026-03-01,,179.00,Monthly,no
```

### Input: `payments.csv`

```csv
Payment ID,Contract ID,Paid At,Amount,Status,Method
P-1,CT-1,2026-07-01 08:01,149.00,Succeeded,Card
P-2,CT-2,2026-07-01 08:02,159.00,Succeeded,ACH
P-3,CT-3,2026-07-02 12:00,179.00,Failed,Card
```

### Input: `attendance.csv`

```csv
Attendance ID,Student ID,Class Name,Checked In At,Points
A-1,S-1,Kids BJJ,2026-07-01 17:55,10
A-2,S-1,Kids BJJ,2026-07-03 17:58,10
A-3,S-2,Teen BJJ,2026-07-02 18:25,15
```

### Input: `rank_history.csv`

```csv
Rank ID,Student ID,Belt,Awarded On,Instructor
R-1,S-1,White Belt,2025-09-01,Coach Kim
R-2,S-1,Gray Belt,2026-06-15,Coach Kim
R-3,S-2,Yellow Belt,2026-05-10,Coach Alvarez
```

### Output

```json
{
  "households": [
    {
      "externalId": "FAM-22",
      "name": "Chen Household",
      "primaryContactId": "crmContact:G-8"
    }
  ],
  "members": [
    {
      "externalId": "S-1",
      "householdId": "household:FAM-22",
      "firstName": "Mia",
      "lastName": "Chen",
      "dateOfBirth": "2014-05-12",
      "status": "active",
      "tags": ["kids-bjj"],
      "guardianContactId": "crmContact:G-8"
    }
  ],
  "memberships": [
    {
      "externalId": "CT-1",
      "memberId": "member:S-1",
      "name": "Kids Unlimited",
      "status": "active",
      "billing": {
        "amount": 14900,
        "currency": "USD",
        "cadence": "monthly",
        "autopay": true
      }
    }
  ],
  "billing": {
    "payments": [
      {
        "externalId": "P-1",
        "membershipId": "membership:CT-1",
        "amount": 14900,
        "currency": "USD",
        "status": "succeeded",
        "method": "card"
      }
    ]
  },
  "attendance": {
    "records": [
      {
        "externalId": "A-1",
        "memberId": "member:S-1",
        "className": "Kids BJJ",
        "checkedInAt": "2026-07-01T17:55:00-04:00",
        "points": 10
      }
    ],
    "memberTotals": [
      {
        "memberId": "member:S-1",
        "attendanceCount": 2,
        "points": 20
      }
    ]
  },
  "rankHistory": [
    {
      "externalId": "R-2",
      "memberId": "member:S-1",
      "rank": "gray-belt",
      "awardedOn": "2026-06-15",
      "awardedBy": "Coach Kim"
    }
  ],
  "reviewQueue": [
    {
      "source": "students.csv",
      "sourceId": "S-3",
      "reason": "Adult member has no emergency contact"
    }
  ]
}
```

### JavaScript

```js
import {
  migrate,
  csv,
  preset,
  parse,
  text
} from "@ourapp/migrate";

const audit = sourceName => entity => entity
  .field("migration.source")
    .value(sourceName)

  .field("migration.sourceRow")
    .compute(row => row.__row);

export default migrate("Complete Academy Migration")
  .read(csv("students.csv"))
  .as("students")

  .read(csv("guardians.csv"))
  .as("guardians")

  .read(csv("contracts.csv"))
  .as("contracts")

  .read(csv("payments.csv"))
  .as("payments")

  .read(csv("attendance.csv"))
  .as("attendance")

  .read(csv("rank_history.csv"))
  .as("ranks")

  .write("crm.contacts", contacts => contacts
    .rows("guardians")
    .key("Guardian ID")
    .use(preset.contact({
      name: "Name",
      email: "Email",
      phone: "Phone"
    }))
    .use(audit("guardians.csv"))
  )

  .write("households", households => households
    .groups("students")
      .by("Household Code")

    .where(group => Boolean(group.key))
    .key(group => group.key)

    .field("name")
      .compute(group => {
        const firstStudent =
          group.rows[0]["Student Name"];

        const familyName =
          parse.name(firstStudent).lastName;

        return `${familyName} Household`;
      })

    .field("primaryContactId")
      .compute((group, ctx) => {
        const guardianId =
          group.rows
            .map(row => row["Guardian ID"])
            .find(Boolean);

        return guardianId
          ? ctx.ref("crm.contacts", guardianId)
          : null;
      })
  )

  .write("members", members => members
    .rows("students")
    .key("Student ID")

    .use(preset.member({
      name: "Student Name",
      email: "Email",
      phone: "Phone",
      dateOfBirth: "DOB"
    }))

    .field("householdId")
      .ref("households")
      .by("Household Code")
      .optional()

    .field("guardianContactId")
      .ref("crm.contacts")
      .by("Guardian ID")
      .optional()

    .field("status")
      .value("active")

    .field("tags")
      .from("Program")
      .map(program => [text.slug(program)])

    .use(audit("students.csv"))

    .review.when(
      row =>
        parse.age(row.DOB) < 18 &&
        !row["Guardian ID"],
      row =>
        `Minor ${row["Student ID"]} has no guardian`
    )

    .review.when(
      row =>
        parse.age(row.DOB) >= 18 &&
        !row["Guardian ID"] &&
        !row.Phone,
      () => "Adult member has no emergency contact"
    )
  )

  .write("memberships", memberships => memberships
    .rows("contracts")
    .key("Contract ID")

    .field("memberId")
      .ref("members")
      .by("Student ID")

    .field("name")
      .from("Plan")

    .field("startsOn")
      .from("Start Date")
      .map(parse.date)

    .field("endsOn")
      .from("End Date")
      .map(parse.optionalDate)

    .field("status")
      .compute(row =>
        row["End Date"] &&
        parse.date(row["End Date"]) < parse.today()
          ? "ended"
          : "active"
      )

    .field("billing")
      .compute(row => ({
        ...parse.money(row.Amount, "USD"),
        cadence: text.slug(row.Cadence),
        autopay: parse.boolean(row.Autopay)
      }))

    .use(audit("contracts.csv"))

    .review.when(
      row => parse.money(row.Amount, "USD").minor <= 0,
      () => "Membership has a non-positive billing amount"
    )
  )

  .write("billing.payments", payments => payments
    .rows("payments")
    .key("Payment ID")

    .field("membershipId")
      .ref("memberships")
      .by("Contract ID")

    .field("paidAt")
      .from("Paid At")
      .map(value =>
        parse.zonedDateTime(
          value,
          "America/New_York"
        )
      )

    .field("amount")
      .from("Amount")
      .map(value =>
        parse.money(value, "USD").minor
      )

    .field("currency")
      .value("USD")

    .field("status")
      .from("Status")
      .map(text.slug)

    .field("method")
      .from("Method")
      .map(text.slug)

    .use(audit("payments.csv"))
  )

  .write("attendance.records", records => records
    .rows("attendance")
    .key("Attendance ID")

    .field("memberId")
      .ref("members")
      .by("Student ID")

    .field("className")
      .from("Class Name")

    .field("checkedInAt")
      .from("Checked In At")
      .map(value =>
        parse.zonedDateTime(
          value,
          "America/New_York"
        )
      )

    .field("points")
      .from("Points")
      .map(value =>
        parse.integer(value, { default: 0 })
      )

    .use(audit("attendance.csv"))
  )

  .write("attendance.memberTotals", totals => totals
    .groups("attendance")
      .by("Student ID")

    .key(group => group.key)

    .field("memberId")
      .compute((group, ctx) =>
        ctx.ref("members", group.key)
      )

    .field("attendanceCount")
      .compute(group => group.rows.length)

    .field("points")
      .compute(group =>
        group.rows.reduce(
          (total, row) =>
            total + parse.integer(row.Points, {
              default: 0
            }),
          0
        )
      )
  )

  .write("rankHistory", ranks => ranks
    .rows("ranks")
    .key("Rank ID")

    .field("memberId")
      .ref("members")
      .by("Student ID")

    .field("rank")
      .from("Belt")
      .map(text.slug)

    .field("awardedOn")
      .from("Awarded On")
      .map(parse.date)

    .field("awardedBy")
      .from("Instructor")

    .use(audit("rank_history.csv"))
  )

  .onConflict("merge")
  .unresolvedReferences("review")
  .invalidRows("review");
```


---

> Make api spec

I’m turning the examples into a formal JavaScript/TypeScript API specification: grammar, types, execution semantics, defaults, errors, and extension points.

Below is a formal API specification for the fluent migration grammar.

:::writing{variant="document" id="48317"}
# `@ourapp/migrate` API Specification

## 1. Purpose

`@ourapp/migrate` is a declarative JavaScript and TypeScript API for transforming third-party business data into the OurApp import model.

It is designed for:

- CSV and JSON source files
- Multi-file migrations
- Schema mapping
- Data normalization
- Joins and grouping
- Entity references
- Deduplication
- Aggregation
- Validation
- Human review queues
- Migration audit trails

The API uses a fluent builder grammar. Opinionated defaults handle common data-cleaning behavior, while lambdas provide complete customization.

---

# 2. Basic Grammar

```ts
migrate(name)
  .read(source)
  .as(alias)

  .write(target, entity =>
    entity
      .rows(sourceAlias)
      .key(sourceColumn)

      .field(targetField)
        .from(sourceColumn)
        .map(transform)
  )

  .onConflict(strategy)
  .invalidRows(strategy)
  .unresolvedReferences(strategy);
```

Example:

```js
import { migrate, csv, preset } from "@ourapp/migrate";

export default migrate("Member Import")
  .read(csv("members.csv"))
  .as("members")

  .write("members", members => members
    .rows("members")
    .key("Member ID")
    .use(preset.member({
      name: "Full Name",
      email: "Email",
      phone: "Phone"
    }))
  );
```

---

# 3. Package Exports

```ts
export {
  migrate,
  csv,
  json,
  source,

  preset,
  parse,
  normalize,
  text,
  date,
  money,

  definePreset,
  defineTransform,
  defineValidator,

  MigrationError
};
```

---

# 4. Top-Level Migration Builder

## `migrate(name, options?)`

Creates a migration definition.

```ts
function migrate(
  name: string,
  options?: MigrationOptions
): MigrationBuilder;
```

```ts
interface MigrationOptions {
  timezone?: string;
  locale?: string;
  currency?: string;
  country?: string;

  strict?: boolean;
  concurrency?: number;

  metadata?: Record<string, unknown>;
}
```

Defaults:

```js
{
  timezone: "UTC",
  locale: "en-US",
  currency: "USD",
  country: "US",
  strict: false,
  concurrency: 4
}
```

Example:

```js
migrate("Legacy Gym Import", {
  timezone: "America/New_York",
  currency: "USD",
  country: "US"
});
```

---

# 5. Reading Sources

## `.read(source)`

Registers an input source.

```ts
read(source: SourceDefinition): PendingSourceBuilder;
```

The source must subsequently be assigned an alias with `.as()`.

```js
migrate("Import")
  .read(csv("members.csv"))
  .as("members");
```

## `.as(alias)`

Assigns a unique alias to the preceding source.

```ts
as(alias: string): MigrationBuilder;
```

Aliases are used by:

- `.rows(alias)`
- `.groups(alias)`
- `.join(alias)`
- `ctx.lookup(alias, ...)`

---

# 6. CSV Sources

## `csv(path, options?)`

```ts
function csv(
  path: string,
  options?: CsvOptions
): SourceDefinition;
```

```ts
interface CsvOptions {
  delimiter?: string;
  quote?: string;
  escape?: string;
  encoding?: string;

  headers?: boolean | string[];
  trimHeaders?: boolean;
  trimValues?: boolean;

  skipEmptyLines?: boolean;
  emptyValue?: null | undefined | string;

  rowNumberField?: string;
}
```

Defaults:

```js
{
  delimiter: ",",
  quote: "\"",
  escape: "\"",
  encoding: "utf-8",

  headers: true,
  trimHeaders: true,
  trimValues: true,

  skipEmptyLines: true,
  emptyValue: null,

  rowNumberField: "__row"
}
```

Example:

```js
csv("members.csv", {
  delimiter: ";",
  encoding: "utf-8"
});
```

---

# 7. JSON Sources

## `json(path, options?)`

```ts
function json(
  path: string,
  options?: JsonOptions
): SourceDefinition;
```

```ts
interface JsonOptions {
  path?: string;
  rowNumberField?: string;
}
```

The `path` option selects an array inside the JSON document.

```js
json("export.json", {
  path: "data.customers"
});
```

Input:

```json
{
  "data": {
    "customers": [
      {
        "id": "C-1",
        "name": "Ana Torres"
      }
    ]
  }
}
```

---

# 8. Custom Sources

## `source(adapter)`

Creates a custom source adapter.

```ts
function source<T>(
  adapter: SourceAdapter<T>
): SourceDefinition;
```

```ts
interface SourceAdapter<T> {
  name?: string;

  read(
    context: SourceContext
  ): AsyncIterable<T> | Promise<T[]> | T[];
}
```

Example:

```js
const apiSource = source({
  name: "legacy-api",

  async read() {
    const response = await fetchLegacyCustomers();
    return response.customers;
  }
});
```

---

# 9. Writing Output Collections

## `.write(target, configure)`

Defines an output collection.

```ts
write(
  target: string,
  configure: (
    builder: EntityBuilder
  ) => EntityBuilder | void
): MigrationBuilder;
```

Targets may be nested paths.

```js
.write("members", ...)
.write("billing.customers", ...)
.write("crm.activities", ...)
.write("attendance.records", ...)
```

The generated output follows the target path:

```json
{
  "billing": {
    "customers": []
  }
}
```

---

# 10. Entity Input Modes

An output entity must choose one input mode.

## `.rows(alias)`

Processes each source row independently.

```ts
rows(sourceAlias: string): EntityBuilder;
```

```js
members.rows("members");
```

## `.groups(alias)`

Groups source rows before processing.

```ts
groups(sourceAlias: string): GroupBuilder;
```

```js
totals
  .groups("attendance")
  .by("Student ID");
```

A group has this structure:

```ts
interface RowGroup<Row = SourceRow> {
  key: unknown;
  rows: Row[];
}
```

## `.from(generator)`

Creates entities using a custom iterable.

```ts
from(
  generator:
    | OutputRow[]
    | Promise<OutputRow[]>
    | ((ctx: MigrationContext) =>
        OutputRow[] | Promise<OutputRow[]>)
): EntityBuilder;
```

---

# 11. Entity Keys

Every output entity should have a stable key.

## `.key(column)`

```ts
key(sourceColumn: string): EntityBuilder;
```

```js
.key("Member ID")
```

## `.key(lambda)`

```ts
key(
  resolver: (
    row: SourceRow,
    ctx: RowContext
  ) => Primitive
): EntityBuilder;
```

```js
.key(row =>
  `${row["Member ID"]}:${row["Plan Code"]}`
)
```

Keys are used for:

- Idempotency
- Conflict detection
- Entity references
- Import previews
- Update matching
- Error reporting

Unless configured otherwise, the output entity identifier is:

```txt
{targetType}:{key}
```

Example:

```txt
member:M-100
membership:C-100:UNLIMITED
```

---

# 12. Field Mapping

## `.field(path)`

Begins a field definition.

```ts
field(path: string): FieldBuilder;
```

Nested paths are supported.

```js
.field("billing.amount")
.field("address.city")
.field("migration.source")
```

---

## `.from(column)`

Copies a source value.

```ts
from(sourcePath: string): FieldBuilder;
```

```js
.field("email")
  .from("Email")
```

Nested joined values may also be referenced:

```js
.field("planName")
  .from("plan.Plan Name")
```

---

## `.value(value)`

Assigns a constant.

```ts
value(
  value: unknown
): FieldBuilder;
```

```js
.field("currency")
  .value("USD")
```

A lambda may be passed for dynamic constants:

```js
.field("importedAt")
  .value(ctx => ctx.startedAt)
```

---

## `.map(transform)`

Transforms the current field value.

```ts
map<Input, Output>(
  transform: (
    value: Input,
    row: SourceRow,
    ctx: RowContext
  ) => Output | Promise<Output>
): FieldBuilder;
```

```js
.field("status")
  .from("Active")
  .map(value =>
    value === "yes" ? "active" : "inactive"
  )
```

Transforms may be chained:

```js
.field("email")
  .from("Email")
  .map(normalize.email)
  .map(value => value || null)
```

---

## `.compute(lambda)`

Computes a field directly from the row.

```ts
compute<Output>(
  resolver: (
    row: SourceRow,
    ctx: RowContext
  ) => Output | Promise<Output>
): FieldBuilder;
```

```js
.field("billing")
  .compute(row => ({
    amount: parse.money(row.Amount).minor,
    currency: "USD",
    cadence: "monthly"
  }))
```

---

## `.default(value)`

Uses a fallback when the mapped value is null, undefined, or empty.

```ts
default(
  value:
    | unknown
    | ((row: SourceRow, ctx: RowContext) => unknown)
): FieldBuilder;
```

```js
.field("status")
  .from("Status")
  .default("active")
```

By default, the following values are considered empty:

```js
null
undefined
""
```

---

## `.required(message?)`

Marks the field as required.

```ts
required(message?: string): FieldBuilder;
```

```js
.field("email")
  .from("Email")
  .map(normalize.email)
  .required("Member email is required")
```

A missing value produces a validation issue.

---

## `.optional()`

Allows a field or reference to resolve to `null`.

```ts
optional(): FieldBuilder;
```

```js
.field("guardianContactId")
  .ref("crm.contacts")
  .by("Guardian ID")
  .optional()
```

---

## `.omitWhen(predicate)`

Omits the field entirely when the predicate returns true.

```ts
omitWhen(
  predicate: (
    value: unknown,
    row: SourceRow,
    ctx: RowContext
  ) => boolean
): FieldBuilder;
```

```js
.field("middleName")
  .from("Middle Name")
  .omitWhen(value => !value)
```

---

## `.validate(validator)`

Adds field-level validation.

```ts
validate(
  validator:
    | Validator
    | ((value: unknown, row: SourceRow, ctx: RowContext) =>
        boolean | string | ValidationResult)
): FieldBuilder;
```

```js
.field("amount")
  .from("Amount")
  .map(value => parse.money(value).minor)
  .validate(value =>
    value > 0 || "Amount must be positive"
  )
```

---

# 13. References

References connect output entities without requiring the final database ID.

## `.ref(target)`

Begins a reference field.

```ts
ref(target: string): ReferenceBuilder;
```

```js
.field("memberId")
  .ref("members")
  .by("Member ID")
```

## `.by(column)`

Uses the current row's source column as the referenced key.

```ts
by(sourceColumn: string): FieldBuilder;
```

```js
.field("memberId")
  .ref("members")
  .by("Student ID")
```

## `.by(lambda)`

Computes the referenced key.

```ts
by(
  resolver: (
    row: SourceRow,
    ctx: RowContext
  ) => Primitive
): FieldBuilder;
```

```js
.field("contactId")
  .ref("crm.contacts")
  .by(row =>
    normalize.email(row.Email) ||
    normalize.phone(row.Phone)
  )
```

## `.through(alias)`

Resolves a reference through an alias registered by `.aliases()`.

```js
.field("contactId")
  .ref("crm.contacts")
  .through("legacyLeadId")
  .by("Lead ID")
```

---

# 14. Reference Aliases

## `.aliases(resolver)`

Registers alternate keys for an output entity.

```ts
aliases(
  resolver: (
    row: SourceRow,
    ctx: RowContext
  ) => Primitive | Primitive[]
): EntityBuilder;
```

Example:

```js
.write("crm.contacts", contacts => contacts
  .rows("prospects")

  .dedupe
    .by(identity)
    .merge(mergeLeads)

  .key(identity)

  .aliases(row =>
    row.__leadIds
  )
)
```

This allows multiple legacy lead IDs to resolve to one contact.

---

# 15. Filtering

## `.where(predicate)`

Includes only matching rows or groups.

```ts
where(
  predicate: (
    row: SourceRow,
    ctx: RowContext
  ) => boolean | Promise<boolean>
): EntityBuilder;
```

```js
.where(row => row.Status !== "Deleted")
```

Multiple `.where()` calls are combined using logical AND.

---

## `.reject(predicate, reason?)`

Rejects matching rows and records an issue.

```ts
reject(
  predicate: RowPredicate,
  reason?: string | ReasonResolver
): EntityBuilder;
```

```js
.reject(
  row => !row["Member ID"],
  "Member ID is missing"
)
```

---

# 16. Joins

## `.join(alias)`

Starts a source join.

```ts
join(sourceAlias: string): JoinBuilder;
```

## `.on(column)`

Joins rows where the same column has the same value.

```js
.join("plans")
  .on("Plan Code")
  .as("plan")
```

Equivalent to:

```js
.join("plans")
  .on({
    left: "Plan Code",
    right: "Plan Code"
  })
  .as("plan")
```

## `.on(config)`

```ts
interface JoinCondition {
  left: string | RowValueResolver;
  right: string | RowValueResolver;
}
```

```js
.join("plans")
  .on({
    left: row => row["Legacy Plan"],
    right: plan => plan.Code
  })
  .as("plan")
```

## `.as(name)`

Assigns a namespace to the joined row.

```js
.field("name")
  .from("plan.Plan Name")
```

## Join types

```js
.join("plans")
  .left()
  .on("Plan Code")
  .as("plan")
```

Supported join types:

```ts
.inner()
.left()
.required()
```

Defaults:

```txt
left join
```

`.required()` creates a review or error when no joined row is found.

---

# 17. Grouping and Aggregation

## `.groups(alias).by(key)`

```js
.write("attendance.memberTotals", totals => totals
  .groups("attendance")
  .by("Student ID")
)
```

The grouping key may be a column or lambda.

```js
.groups("payments")
.by(row => `${row.Customer}:${row.Month}`)
```

## Group output

```js
.field("attendanceCount")
  .compute(group => group.rows.length)

.field("points")
  .compute(group =>
    group.rows.reduce(
      (sum, row) => sum + parse.integer(row.Points),
      0
    )
  )
```

---

# 18. Deduplication

## `.dedupe.by(key)`

Groups logically identical rows before mapping.

```ts
dedupe: {
  by(
    key:
      | string
      | ((row: SourceRow, ctx: RowContext) => Primitive)
  ): DedupeBuilder;
}
```

```js
.dedupe
  .by(row =>
    normalize.email(row.Email) ||
    normalize.phone(row.Phone)
  )
```

## `.merge(lambda)`

Defines how duplicate rows are combined.

```ts
merge(
  resolver: (
    current: SourceRow,
    incoming: SourceRow,
    ctx: MergeContext
  ) => SourceRow
): EntityBuilder;
```

```js
.dedupe
  .by(identity)
  .merge((current, incoming) => ({
    ...current,
    Email: current.Email || incoming.Email,
    Phone: current.Phone || incoming.Phone
  }))
```

Default merge strategy:

- First non-empty scalar wins
- Arrays are concatenated
- Objects are shallow merged
- Earlier source row remains canonical
- Conflicting non-empty scalar values generate a warning

---

# 19. Presets

Presets contain reusable field mappings and normalization rules.

## `.use(preset)`

```ts
use(
  extension:
    | EntityExtension
    | ((builder: EntityBuilder) => EntityBuilder | void)
): EntityBuilder;
```

```js
.use(preset.member({
  name: "Student Name",
  email: "Email",
  phone: "Phone"
}))
```

## Built-in presets

```ts
preset.member(options)
preset.contact(options)
preset.address(options)
preset.membership(options)
preset.payment(options)
preset.classSeries(options)
preset.booking(options)
```

## `preset.member(options)`

```ts
interface MemberPresetOptions {
  name?: string;
  firstName?: string;
  lastName?: string;

  email?: string;
  phone?: string;
  dateOfBirth?: string;

  status?: string;
  externalId?: string;

  country?: string;
}
```

Behavior:

- Splits full names
- Lowercases and validates emails
- Normalizes phone numbers
- Parses dates
- Trims whitespace
- Converts blank strings to null
- Uses the migration country for phone normalization

Example:

```js
.use(preset.member({
  name: "Student Name",
  email: "Email",
  phone: "Phone",
  dateOfBirth: "DOB"
}))
```

Equivalent conceptual output:

```js
.field("firstName")
  .from("Student Name")
  .map(value => parse.name(value).firstName)

.field("lastName")
  .from("Student Name")
  .map(value => parse.name(value).lastName)

.field("email")
  .from("Email")
  .map(normalize.email)

.field("phone")
  .from("Phone")
  .map(normalize.phone)

.field("dateOfBirth")
  .from("DOB")
  .map(parse.optionalDate)
```

---

# 20. Custom Presets

## `definePreset(factory)`

```ts
function definePreset<Options>(
  factory: (
    options: Options
  ) => EntityExtension
): (options: Options) => EntityExtension;
```

Example:

```js
const audited = definePreset(sourceName => entity =>
  entity
    .field("migration.source")
      .value(sourceName)

    .field("migration.row")
      .compute(row => row.__row)
);
```

Usage:

```js
.use(audited("members.csv"))
```

---

# 21. Row-Level Review Rules

## `.review.when(predicate, reason)`

Adds a row to the human review queue when the condition is true.

```ts
review: {
  when(
    predicate: (
      row: SourceRow,
      ctx: RowContext
    ) => boolean | Promise<boolean>,

    reason:
      | string
      | ((row: SourceRow, ctx: RowContext) => string)
  ): EntityBuilder;
}
```

```js
.review.when(
  row =>
    parse.age(row.DOB) < 18 &&
    !row["Guardian ID"],

  row =>
    `Minor ${row["Student ID"]} has no guardian`
)
```

Review rules do not discard the output entity unless explicitly configured.

---

## `.review.field(path, reason)`

Marks a specific field for review.

```js
.review.field(
  "billing.amount",
  "Legacy amount differs from plan price"
)
```

---

## `.review.score(lambda)`

Attaches a confidence score.

```js
.review.score((row, output) => {
  let score = 1;

  if (!output.email) score -= 0.2;
  if (!output.phone) score -= 0.2;
  if (!output.dateOfBirth) score -= 0.1;

  return score;
})
```

Confidence scores must be between `0` and `1`.

---

# 22. Entity Validation

## `.validate(validator)`

Adds output-level validation.

```ts
validate(
  validator: (
    output: OutputEntity,
    row: SourceRow,
    ctx: RowContext
  ) =>
    | boolean
    | string
    | ValidationResult
    | Promise<boolean | string | ValidationResult>
): EntityBuilder;
```

```js
.validate(member => {
  if (!member.email && !member.phone) {
    return "Member requires an email or phone";
  }

  return true;
})
```

---

# 23. Transformation Context

Lambdas receive a context object.

```ts
interface RowContext {
  migration: {
    name: string;
    timezone: string;
    locale: string;
    currency: string;
    country: string;
  };

  source: {
    alias: string;
    file?: string;
    rowNumber?: number;
  };

  startedAt: string;

  lookup(
    sourceAlias: string,
    keyColumn: string,
    keyValue: unknown
  ): SourceRow | undefined;

  lookupMany(
    sourceAlias: string,
    keyColumn: string,
    keyValue: unknown
  ): SourceRow[];

  ref(
    target: string,
    key: Primitive
  ): EntityReference;

  canRef(
    target: string,
    sourceColumnOrKey: string,
    value?: Primitive
  ): boolean;

  warn(
    message: string,
    details?: Record<string, unknown>
  ): void;

  review(
    reason: string,
    details?: Record<string, unknown>
  ): void;

  reject(
    reason: string,
    details?: Record<string, unknown>
  ): never;
}
```

Example:

```js
.field("startsAt")
  .compute((row, ctx) => {
    const classRow = ctx.lookup(
      "classes",
      "Class ID",
      row["Class ID"]
    );

    return parse.zonedDateTime({
      date: row.Date,
      time: classRow["Start Time"],
      timezone: classRow.Timezone
    });
  })
```

---

# 24. Parsing Utilities

## `parse.boolean(value, options?)`

```ts
parse.boolean(
  value: unknown,
  options?: {
    trueValues?: unknown[];
    falseValues?: unknown[];
    default?: boolean | null;
  }
): boolean | null;
```

Default true values:

```js
[
  true,
  1,
  "1",
  "true",
  "yes",
  "y",
  "on",
  "active"
]
```

Default false values:

```js
[
  false,
  0,
  "0",
  "false",
  "no",
  "n",
  "off",
  "inactive"
]
```

---

## `parse.integer(value, options?)`

```ts
parse.integer(
  value: unknown,
  options?: {
    default?: number | null;
    min?: number;
    max?: number;
  }
): number | null;
```

---

## `parse.decimal(value, options?)`

```ts
parse.decimal(
  value: unknown,
  options?: {
    default?: number | null;
  }
): number | null;
```

---

## `parse.money(value, currency?)`

```ts
interface MoneyValue {
  amount: number;
  minor: number;
  currency: string;
}
```

```js
parse.money("$149.00", "USD");
```

Returns:

```json
{
  "amount": 149,
  "minor": 14900,
  "currency": "USD"
}
```

---

## `parse.date(value, options?)`

Returns an ISO calendar date.

```js
parse.date("7/1/2026");
```

Returns:

```txt
2026-07-01
```

---

## `parse.optionalDate(value, options?)`

Returns `null` for blank values.

```js
parse.optionalDate("");
```

Returns:

```js
null
```

---

## `parse.zonedDateTime(value, timezone?)`

Returns an ISO 8601 timestamp containing an offset.

```js
parse.zonedDateTime(
  "2026-07-01 17:55",
  "America/New_York"
);
```

Returns:

```txt
2026-07-01T17:55:00-04:00
```

Object form:

```js
parse.zonedDateTime({
  date: "2026-07-01",
  time: "17:55",
  timezone: "America/New_York"
});
```

---

## `parse.name(value)`

```ts
interface ParsedName {
  firstName: string | null;
  middleName: string | null;
  lastName: string | null;
  suffix: string | null;
  displayName: string | null;
}
```

---

## `parse.age(dateOfBirth, atDate?)`

```ts
parse.age(
  dateOfBirth: unknown,
  atDate?: Date | string
): number;
```

---

## `parse.weekday(value)`

Normalizes weekday abbreviations.

```js
parse.weekday("Wed");
```

Returns:

```txt
wednesday
```

---

# 25. Normalization Utilities

## `normalize.email(value)`

```js
normalize.email(" ANA@EXAMPLE.COM ");
```

Returns:

```txt
ana@example.com
```

Invalid addresses return `null` unless strict parsing is enabled.

---

## `normalize.phone(value, country?)`

```js
normalize.phone("(512) 555-0198", "US");
```

Returns:

```txt
+15125550198
```

---

## `normalize.whitespace(value)`

Collapses repeated whitespace and trims the result.

---

## `normalize.empty(value)`

Converts empty strings and whitespace-only strings to `null`.

---

# 26. Text Utilities

## `text.slug(value)`

```js
text.slug("Kids BJJ");
```

Returns:

```txt
kids-bjj
```

## `text.title(value)`

```js
text.title("MUAY THAI");
```

Returns:

```txt
Muay Thai
```

## `text.upper(value)`

## `text.lower(value)`

## `text.truncate(value, length)`

---

# 27. Conflict Strategies

## `.onConflict(strategy)`

Controls behavior when an output key appears more than once.

```ts
type ConflictStrategy =
  | "error"
  | "first"
  | "last"
  | "merge"
  | "review";
```

```js
.onConflict("merge")
```

Defaults:

```txt
review
```

Behavior:

| Strategy | Behavior |
|---|---|
| `error` | Stops the migration |
| `first` | Keeps the first entity |
| `last` | Keeps the last entity |
| `merge` | Merges compatible fields |
| `review` | Keeps the first entity and creates a review issue |

A custom strategy may be supplied:

```js
.onConflict((current, incoming, ctx) => ({
  ...current,
  ...incoming,
  tags: [
    ...new Set([
      ...(current.tags || []),
      ...(incoming.tags || [])
    ])
  ]
}))
```

---

# 28. Invalid Row Strategies

## `.invalidRows(strategy)`

```ts
type InvalidRowStrategy =
  | "error"
  | "skip"
  | "review"
  | "include";
```

```js
.invalidRows("review")
```

Default:

```txt
review
```

---

# 29. Unresolved Reference Strategies

## `.unresolvedReferences(strategy)`

```ts
type UnresolvedReferenceStrategy =
  | "error"
  | "null"
  | "skip"
  | "review";
```

```js
.unresolvedReferences("review")
```

Default:

```txt
review
```

---

# 30. Unknown Columns

## `.unknownColumns(strategy)`

Controls source columns that are never consumed.

```ts
type UnknownColumnStrategy =
  | "ignore"
  | "warn"
  | "review"
  | "error";
```

```js
.unknownColumns("warn")
```

Default:

```txt
ignore
```

---

# 31. Execution

A migration definition is executable.

## `.run(input?)`

```ts
run(
  options?: RunOptions
): Promise<MigrationResult>;
```

```ts
interface RunOptions {
  mode?: "preview" | "commit";
  limit?: number;

  includeSourceRows?: boolean;
  includeAudit?: boolean;

  signal?: AbortSignal;
}
```

Example:

```js
const result = await migration.run({
  mode: "preview",
  includeAudit: true
});
```

---

# 32. Migration Result

```ts
interface MigrationResult {
  migration: {
    name: string;
    startedAt: string;
    completedAt: string;
    durationMs: number;
    mode: "preview" | "commit";
  };

  output: Record<string, unknown>;

  summary: {
    sourceRows: number;
    outputEntities: number;
    acceptedRows: number;
    skippedRows: number;
    reviewRows: number;
    errorRows: number;
    warnings: number;
  };

  collections: Record<
    string,
    {
      created: number;
      updated: number;
      unchanged: number;
      skipped: number;
      reviewed: number;
      failed: number;
    }
  >;

  reviewQueue: ReviewIssue[];
  warnings: MigrationIssue[];
  errors: MigrationIssue[];
}
```

Example:

```json
{
  "migration": {
    "name": "Legacy Gym Import",
    "startedAt": "2026-08-01T14:00:00Z",
    "completedAt": "2026-08-01T14:00:04Z",
    "durationMs": 4210,
    "mode": "preview"
  },
  "summary": {
    "sourceRows": 12040,
    "outputEntities": 18320,
    "acceptedRows": 11890,
    "skippedRows": 20,
    "reviewRows": 125,
    "errorRows": 5,
    "warnings": 31
  }
}
```

---

# 33. Review Issue Structure

```ts
interface ReviewIssue {
  id: string;

  severity:
    | "info"
    | "warning"
    | "error";

  target?: string;
  outputKey?: string;
  field?: string;

  sourceAlias?: string;
  sourceFile?: string;
  sourceRow?: number;
  sourceId?: string;

  reason: string;

  input?: unknown;
  proposedOutput?: unknown;

  metadata?: Record<string, unknown>;
}
```

Example:

```json
{
  "id": "review_01J...",
  "severity": "warning",
  "target": "members",
  "outputKey": "S-3",
  "field": "guardianContactId",
  "sourceAlias": "students",
  "sourceFile": "students.csv",
  "sourceRow": 4,
  "sourceId": "S-3",
  "reason": "Adult member has no emergency contact"
}
```

---

# 34. Execution Order

A migration executes in these phases:

1. Read and parse sources
2. Normalize source headers and empty values
3. Build source indexes
4. Apply source-level validation
5. Execute output collections in declaration order
6. Resolve joins
7. Apply filters
8. Apply deduplication
9. Generate entity keys
10. Map output fields
11. Resolve references
12. Apply field validation
13. Apply entity validation
14. Evaluate review rules
15. Detect conflicts
16. Produce preview or commit plan
17. Return output and review results

Output collections may reference collections declared later. Reference resolution occurs after entity keys have been indexed.

---

# 35. Deterministic Behavior

Given identical:

- Source data
- Migration definition
- Package version
- Runtime options

The migration must produce identical:

- Entity keys
- Output values
- Review issues
- Conflict decisions
- Collection ordering

Output entities retain source order unless grouping, deduplication, or explicit sorting changes it.

---

# 36. Sorting

## `.sortBy(columnOrLambda, direction?)`

```js
.sortBy("Created At", "asc")
```

```js
.sortBy(
  row => parse.date(row.Date),
  "desc"
)
```

Supported directions:

```ts
"asc" | "desc"
```

---

# 37. Hooks

## `.beforeAll(lambda)`

```js
.beforeAll(async ctx => {
  ctx.metadata.startedBy = "migration-service";
})
```

## `.afterAll(lambda)`

```js
.afterAll(async (result, ctx) => {
  await saveMigrationReport(result);
})
```

## `.beforeCollection(lambda)`

## `.afterCollection(lambda)`

## `.onIssue(lambda)`

```js
.onIssue(issue => {
  console.warn(issue.reason);
})
```

Hooks should not change deterministic mapping results unless explicitly configured as transforms.

---

# 38. Error Model

```ts
class MigrationError extends Error {
  code: MigrationErrorCode;
  source?: SourceLocation;
  target?: string;
  field?: string;
  details?: Record<string, unknown>;
}
```

Core error codes:

```ts
type MigrationErrorCode =
  | "SOURCE_NOT_FOUND"
  | "SOURCE_PARSE_ERROR"
  | "DUPLICATE_SOURCE_ALIAS"
  | "UNKNOWN_SOURCE_ALIAS"
  | "DUPLICATE_OUTPUT_TARGET"
  | "MISSING_ENTITY_KEY"
  | "INVALID_ENTITY_KEY"
  | "FIELD_TRANSFORM_ERROR"
  | "FIELD_VALIDATION_ERROR"
  | "ENTITY_VALIDATION_ERROR"
  | "JOIN_NOT_FOUND"
  | "JOIN_MULTIPLE_MATCHES"
  | "REFERENCE_NOT_FOUND"
  | "REFERENCE_AMBIGUOUS"
  | "OUTPUT_CONFLICT"
  | "INVALID_CONFIGURATION";
```

---

# 39. TypeScript Row Typing

Source and output types may be supplied explicitly.

```ts
interface LegacyMember {
  "Member ID": string;
  "Student Name": string;
  Email?: string;
  Phone?: string;
}

interface MemberOutput {
  externalId: string;
  firstName: string;
  lastName: string;
  email: string | null;
  phone: string | null;
}

const migration = migrate("Typed Import")
  .read(csv<LegacyMember>("members.csv"))
  .as("members")

  .write<LegacyMember, MemberOutput>(
    "members",
    members => members
      .rows("members")
      .key("Member ID")

      .field("externalId")
        .from("Member ID")

      .field("firstName")
        .compute(row =>
          parse.name(row["Student Name"]).firstName
        )
  );
```

---

# 40. Complete Example

```js
import {
  migrate,
  csv,
  preset,
  parse,
  normalize,
  text
} from "@ourapp/migrate";

const memberStatus = value => ({
  active: "active",
  paused: "paused",
  cancelled: "cancelled",
  canceled: "cancelled"
})[text.slug(value)] ?? "inactive";

export default migrate("CrossFit Migration", {
  timezone: "America/New_York",
  country: "US",
  currency: "USD"
})

  .read(csv("clients.csv"))
  .as("clients")

  .read(csv("plans.csv"))
  .as("plans")

  .read(csv("payments.csv"))
  .as("payments")

  .write("members", members => members
    .rows("clients")
    .key("Client ID")

    .use(preset.member({
      name: "Name",
      email: "Email",
      phone: "Phone"
    }))

    .field("externalId")
      .from("Client ID")

    .field("status")
      .from("Status")
      .map(memberStatus)

    .field("tags")
      .from("Program")
      .map(value =>
        value ? [text.slug(value)] : []
      )

    .review.when(
      row =>
        !normalize.email(row.Email) &&
        !normalize.phone(row.Phone, "US"),

      "Member has no valid email or phone"
    )
  )

  .write("memberships", memberships => memberships
    .rows("clients")

    .join("plans")
      .required()
      .on("Plan Code")
      .as("plan")

    .key(row =>
      `${row["Client ID"]}:${row["Plan Code"]}`
    )

    .field("memberId")
      .ref("members")
      .by("Client ID")

    .field("name")
      .from("plan.Plan Name")

    .field("startsOn")
      .from("Start Date")
      .map(parse.date)

    .field("status")
      .from("Status")
      .map(memberStatus)

    .field("billing")
      .compute(row => ({
        amount: parse.money(
          row["plan.Monthly Price"],
          "USD"
        ).minor,

        currency: "USD",
        cadence: "monthly",

        chargeDay: parse.integer(
          row["plan.Billing Day"]
        ),

        autopay: parse.boolean(row.Autopay)
      }))
  )

  .write("billing.payments", payments => payments
    .rows("payments")
    .key("Payment ID")

    .field("membershipId")
      .ref("memberships")
      .by(row =>
        `${row["Client ID"]}:${row["Plan Code"]}`
      )

    .field("amount")
      .from("Amount")
      .map(value =>
        parse.money(value, "USD").minor
      )

    .field("currency")
      .value("USD")

    .field("status")
      .from("Status")
      .map(text.slug)

    .field("paidAt")
      .from("Paid At")
      .map(value =>
        parse.zonedDateTime(
          value,
          "America/New_York"
        )
      )
  )

  .onConflict("review")
  .invalidRows("review")
  .unresolvedReferences("review")
  .unknownColumns("warn");
```

---

# 41. Recommended Naming Conventions

Source aliases:

```txt
members
contracts
payments
classes
attendance
guardians
prospects
notes
```

Output targets:

```txt
members
households
memberships
classSeries
classBookings
billing.customers
billing.payments
crm.contacts
crm.opportunities
crm.activities
attendance.records
attendance.memberTotals
rankHistory
```

Output field names should use camel case:

```txt
externalId
firstName
lastName
dateOfBirth
startsOn
endsOn
checkedInAt
autopayEnabled
```

---

# 42. Core Design Principles

The API follows these rules:

1. Source files are explicitly named and aliased.
2. Every output collection is independently composable.
3. Every output entity has a deterministic key.
4. Common transformations use presets.
5. Business-specific behavior uses lambdas.
6. References use stable migration keys rather than database IDs.
7. Invalid or ambiguous data defaults to human review.
8. Source lineage is retained throughout execution.
9. Preview and commit use the same migration definition.
10. Migrations are deterministic and idempotent.
:::

This can serve as the foundation for implementation, generated TypeScript declarations, and migration authoring documentation.


---

> [image: sediment://file_00000000af90822fb0c2665cfa1eef92]
> [image: sediment://file_0000000024f881fbaeedc97c17b0d8ae]
> Left is company a with guardians = subaccounts, right is ideal representation.
>
> Write the js transform , MvP (no conflict resolution for so)

```unknown
from PIL import Image
for p in ["/mnt/data/IMG_5C41C3E5-44DD-48F4-BD9E-61B6432388BD.jpeg","/mnt/data/IMG_FB527A93-82A3-4C6F-91D3-405593E4D43F.jpeg"]:
    im=Image.open(p)
    print(p, im.size)

```

<details><summary>💭 Thinking</summary>

**Transformed guardians into subaccounts**

**Designing the transformation**

I’m preparing a concise MVP transform from Company A’s CSV into the ideal schema. I’m treating members and guardians as user records, linking dependents through “Sub Account Of,” and avoiding conflict-resolution logic for now.

**Designed the transformation**

**Clarifying guardian links**

I’m assuming each row represents a person, while “Guardian(s)” identifies the parent account. I’ll match guardian names to existing rows, link dependents to the first exact match, and leave unresolved cases untouched for this MVP.

**Clarified guardian links**

</details>

## MVP assumptions

Each Company A row represents one user. `Guardian(s)` contains semicolon-separated names. The guardian also exists as another row in the export. The child’s `subAccountOf` value becomes the guardian’s normalized email, matching the ideal format.

Multiple guardians use the first resolvable guardian. Missing guardians remain `null`. Duplicate IDs fail; there is no deduplication, fuzzy matching, merging, or conflict resolution.

```js
import {
  migrate,
  csv,
  normalize,
  text
} from "@ourapp/migrate";

const columns = {
  user: "User",
  firstName: "First Name",
  lastName: "Last Name",
  email: "Email",
  phone: "SMS Phone",
  status: "Status",
  guardians: "Guardian(s)"
};

const clean = value =>
  String(value ?? "")
    .trim()
    .replace(/\s+/g, " ");

const nameKey = value =>
  clean(value)
    .toLowerCase()
    .replace(/[.'’,-]/g, "");

const rowName = row =>
  clean(`${row[columns.firstName] ?? ""} ${row[columns.lastName] ?? ""}`);

const splitGuardians = value =>
  clean(value)
    .split(/\s*;\s*|\s+\band\b\s+/i)
    .map(clean)
    .filter(Boolean);

const mapStatus = value => {
  const status = text.slug(value ?? "");

  if (!status) return "Active";

  return [
    "active",
    "current",
    "enabled",
    "yes",
    "true",
    "1"
  ].includes(status)
    ? "Active"
    : "Inactive";
};

export default migrate("Company A → Users", {
  country: "US",
  currency: "USD"
})
  .read(csv("company-a.csv"))
  .as("companyA")

  .write("users", users => users
    /*
     * Enrich each source row with its target parent email.
     *
     * ctx.rows(alias) returns all loaded rows for the named source.
     */
    .from(ctx => {
      const rows = ctx.rows("companyA");

      // MVP assumes full names uniquely identify guardian rows.
      const usersByName = new Map(
        rows
          .map(row => [nameKey(rowName(row)), row])
          .filter(([key]) => Boolean(key))
      );

      return rows.map(row => {
        const guardian = splitGuardians(row[columns.guardians])
          .map(name => usersByName.get(nameKey(name)))
          .find(Boolean);

        return {
          ...row,

          // Target screenshot represents ownership using guardian email.
          __subAccountOf: guardian
            ? normalize.email(guardian[columns.email])
            : null
        };
      });
    })

    .key(columns.user)

    .field("user")
      .from(columns.user)
      .required("User ID is required")

    .field("firstName")
      .from(columns.firstName)
      .map(clean)
      .required("First name is required")

    .field("lastName")
      .from(columns.lastName)
      .map(clean)
      .required("Last name is required")

    .field("email")
      .from(columns.email)
      .map(normalize.email)

    .field("subAccountOf")
      .from("__subAccountOf")

    .field("phone")
      .from(columns.phone)
      .map(value => normalize.phone(value, "US"))

    .field("status")
      .from(columns.status)
      .map(mapStatus)
  )

  // MVP: do not merge or resolve duplicate user IDs.
  .onConflict("error")

  // MVP: malformed required rows stop the migration.
  .invalidRows("error");
```

### Resulting output shape

```json
{
  "users": [
    {
      "user": "5704217",
      "firstName": "Paula",
      "lastName": "A",
      "email": "nurse_paularea@yahoo.com",
      "subAccountOf": null,
      "phone": "+19314454242",
      "status": "Active"
    },
    {
      "user": "10429",
      "firstName": "Joanne",
      "lastName": "Bailey",
      "email": "klitch@gmail.com",
      "subAccountOf": "guardian@example.com",
      "phone": "+19313677496",
      "status": "Active"
    }
  ]
}
```

For CSV serialization, the target field order is:

```js
const outputColumns = {
  user: "User",
  firstName: "First Name",
  lastName: "Last Name",
  email: "Email",
  subAccountOf: "Sub Account Of",
  phone: "Phone",
  status: "Status"
};
```

