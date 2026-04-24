---
name: owasp-top-10
description: OWASP Top 10 for Web Applications (2025) vulnerability knowledge base for identifying, assessing, and remediating security risks in web application environments - Brought to you by microsoft/hve-core.
license: CC-BY-SA-4.0
user-invocable: false
metadata:
  authors: "OWASP Web Application Security Project"
  spec_version: "1.0"
  framework_revision: "1.0.0"
  last_updated: "2026-02-13"
  skill_based_on: "https://github.com/chris-buckley/agnostic-prompt-standard"
  content_based_on: "https://owasp.org/Top10/2025/"
---

# OWASP® Top 10 — Skill Entry

This `SKILL.md` is the **entrypoint** for the OWASP Top 10 skill.

The skill encodes the **OWASP Top 10 for Web Applications (2025)** as structured, machine-readable references that an agent can query to identify, assess, and remediate web application security risks.

## Normative references (Web Top 10)

1. A01 — Broken Access Control
2. A02 — Security Misconfiguration
3. A03 — Software and Data Integrity Failures (Supply Chain)
4. A04 — Cryptographic Failures
5. A05 — Injection
6. A06 — Insecure Design
7. A07 — Identification and Authentication Failures
8. A08 — Software and Data Integrity Failures
9. A09 — Security Logging and Monitoring Failures
10. A10 — Server-Side Request Forgery (SSRF)

---

## A01 — Broken Access Control

**Description:** Access control enforces policies so users cannot act outside their intended permissions. Failures lead to unauthorized information disclosure, modification, or destruction.

**Common weaknesses:**
- Bypassing access control checks by modifying the URL, internal app state, or HTML page
- Permitting primary key to be changed to another user's record
- Elevation of privilege (acting as admin without being logged in)
- CORS misconfiguration allowing unauthorized API access
- Force browsing to authenticated pages or accessing privileged endpoints

**Detection (ASP.NET Core):**
- Check that `[Authorize]` attributes are applied on all sensitive controllers/actions
- Verify role checks are enforced server-side (never only on the client)
- Review CORS policy in `Program.cs` — avoid `AllowAnyOrigin` in production
- Confirm object-level authorization: validate that the user owns the resource before CRUD

**Remediation:**
- Use ASP.NET Core built-in authorization policies (`[Authorize(Policy = "...")]`)
- Deny access by default; explicitly allow
- Log access control failures and alert on repeated failures
- Invalidate JWT tokens server-side on logout

---

## A02 — Security Misconfiguration

**Description:** The most common issue. Results from insecure default configurations, incomplete setups, open cloud storage, misconfigured HTTP headers, verbose error messages.

**Common weaknesses:**
- Default credentials unchanged
- Unnecessary features enabled (e.g., Swagger in production)
- Verbose error messages exposing stack traces
- Missing security headers (CSP, HSTS, X-Frame-Options)
- Outdated software or unpatched dependencies

**Detection (ASP.NET Core):**
- Check `app.UseDeveloperExceptionPage()` is only in Development
- Verify `app.UseHsts()` is in production
- Confirm `app.UseHttpsRedirection()` is enabled
- Check security headers with tools like securityheaders.com

**Remediation:**
- Use `app.UseExceptionHandler("/Error")` in production
- Add security headers via middleware:
  ```csharp
  app.Use(async (ctx, next) => {
      ctx.Response.Headers.Add("X-Content-Type-Options", "nosniff");
      ctx.Response.Headers.Add("X-Frame-Options", "DENY");
      ctx.Response.Headers.Add("Referrer-Policy", "no-referrer");
      await next();
  });
  ```
- Disable Swagger/OpenAPI in production environments

---

## A03 — Injection

**Description:** Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query (SQL, OS, LDAP, etc.).

**Common weaknesses:**
- SQL injection via concatenated queries
- OS command injection
- LDAP / XML / JSON injection
- Stored and reflected XSS

**Detection (ASP.NET Core + EF Core):**
- Look for raw SQL with string concatenation: `context.Database.ExecuteSqlRaw($"... {input}")`
- Check for `Html.Raw()` usage without sanitization in Razor views

**Remediation:**
- Use EF Core LINQ queries (parameterized by default)
- If raw SQL is needed, use parameterized form:
  ```csharp
  context.Database.ExecuteSqlRaw("SELECT * FROM Users WHERE Id = {0}", userId);
  // or
  context.Database.ExecuteSqlInterpolated($"SELECT * FROM Users WHERE Id = {userId}");
  ```
- Use `@Html.Encode()` / `@Model.Property` (auto-encoded by Razor) for output
- Never use `Html.Raw()` with user input

---

## A04 — Insecure Design

**Description:** Missing or ineffective security controls by design, not just implementation flaws. Requires threat modeling and secure design principles.

**Common weaknesses:**
- Missing rate limiting on sensitive actions (login, password reset)
- Business logic flaws (e.g., user can manipulate prices)
- No separation between authentication and authorization logic

**Remediation (ASP.NET Core):**
- Implement rate limiting: `builder.Services.AddRateLimiter(...)`
- Model all threat scenarios in design phase
- Apply defense-in-depth: multiple layers of controls

---

## A05 — Cryptographic Failures

**Description:** Data exposed in transit or at rest due to weak/absent cryptography. Previously called "Sensitive Data Exposure".

**Common weaknesses:**
- Passwords stored as plain text or MD5/SHA1 hashes
- Data transmitted over HTTP (not HTTPS)
- Weak random number generation
- Outdated/weak cipher suites (SSL, TLS 1.0/1.1, RC4)

**Detection (ASP.NET Core):**
- Confirm password hashing uses `PasswordHasher<T>` (ASP.NET Core Identity) or BCrypt/Argon2
- Verify `app.UseHttpsRedirection()` is active
- Check for secrets stored in code or `appsettings.json` committed to source control

**Remediation:**
- Use ASP.NET Core Data Protection API for encrypting stored data
- Use `IPasswordHasher<T>` for passwords
- Store secrets in environment variables, Azure Key Vault, or User Secrets
- Never log sensitive data (passwords, tokens, PII)

---

## A06 — Vulnerable and Outdated Components

**Description:** Using components with known vulnerabilities (libraries, frameworks, OS).

**Remediation:**
- Regularly run `dotnet list package --vulnerable`
- Keep NuGet packages updated
- Use GitHub Dependabot or similar automated tools
- Remove unused packages from `.csproj` files

---

## A07 — Identification and Authentication Failures

**Description:** Weaknesses in authentication allow attackers to assume users' identities.

**Common weaknesses:**
- Weak or default passwords permitted
- No brute-force protection
- Weak session management (predictable tokens, no expiry)
- Missing MFA on sensitive functions

**Detection (ASP.NET Core):**
- Check cookie authentication settings: `SlidingExpiration`, `ExpireTimeSpan`
- Verify anti-CSRF tokens on POST forms: `@Html.AntiForgeryToken()` + `[ValidateAntiForgeryToken]`
- Check lockout settings in Identity or custom auth

**Remediation:**
- Implement account lockout after N failed attempts
- Set reasonable session expiry
- Always use `[ValidateAntiForgeryToken]` on state-modifying actions
- Use HTTPS-only, Secure, HttpOnly cookies:
  ```csharp
  builder.Services.ConfigureApplicationCookie(options => {
      options.Cookie.HttpOnly = true;
      options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
      options.Cookie.SameSite = SameSiteMode.Strict;
      options.ExpireTimeSpan = TimeSpan.FromMinutes(30);
      options.SlidingExpiration = true;
  });
  ```

---

## A08 — Software and Data Integrity Failures

**Description:** Code and infrastructure that does not protect against integrity violations (insecure deserialization, untrusted plugins/CDNs).

**Remediation (ASP.NET Core):**
- Use `System.Text.Json` over `Newtonsoft.Json` where possible (safer defaults)
- Validate all deserialized objects
- Use Subresource Integrity (SRI) for external CDN scripts

---

## A09 — Security Logging and Monitoring Failures

**Description:** Insufficient logging and monitoring allows breaches to go undetected.

**Common weaknesses:**
- Login failures not logged
- No alerts on suspicious activity
- Logs stored only locally (vulnerable to tampering)

**Remediation (ASP.NET Core):**
- Log all authentication events (success/failure), access control failures
- Use structured logging (Serilog / NLog / Microsoft.Extensions.Logging)
- Never log sensitive data (passwords, full card numbers, tokens)
- Example:
  ```csharp
  _logger.LogWarning("Failed login attempt for user {UserId} from IP {IP}", userId, ip);
  ```

---

## A10 — Server-Side Request Forgery (SSRF)

**Description:** The app fetches a remote resource based on user-supplied URL without validating it, allowing attackers to access internal services.

**Remediation (ASP.NET Core):**
- Validate and allowlist target URLs before making HTTP requests
- Never pass raw user input to `HttpClient` as a URL
- Use network-level controls to restrict outbound traffic from the server

---

## Skill layout

- `SKILL.md` — this file (skill entrypoint, self-contained).

## Third-Party Attribution

Copyright © OWASP Foundation. OWASP® Top 10 (2025) content is derived from works by the OWASP Foundation, licensed under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Source: https://owasp.org/Top10/2025/. OWASP® is a registered trademark of the OWASP Foundation. Use does not imply endorsement.

Source repository: https://github.com/microsoft/hve-core
