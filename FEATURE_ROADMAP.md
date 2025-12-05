# SafariSmart Feature Roadmap
## Prioritized Development Plan

**Last Updated:** December 5, 2025

---

## URGENT: AWS Deployment (Before Presentation)

**Deadline:** Next week (before presentation)
**Status:** Critical priority
**Estimated Time:** 2-3 days

**Why This is Urgent:**
- Have a presentation next week that requires live demo
- Render database expires December 19
- Need professional deployment for presentation
- Must solve cold start and media persistence issues

**Quick Deployment Plan:**
1. **Day 1:** Terraform setup + infrastructure deployment (4-6 hours)
2. **Day 2:** Application deployment + database migration (4-6 hours)
3. **Day 3:** Testing + domain setup (2-3 hours)

**See:** [AWS_DEPLOYMENT_PLAN.md](AWS_DEPLOYMENT_PLAN.md) for full details

---

## Development Priority Order

### Priority 1: Email Notifications (2-3 days)
### Priority 2: User Dashboard Enhancements (4-5 days)
### Priority 3: Itinerary Sharing (2-3 days)
### Priority 4: Trip Management (3-4 days)

---

## Priority 1: Critical Features (Build First)

### 1.1 Email Notifications Integration
**Status:** System exists, needs integration
**Estimated Time:** 2-3 days
**Impact:** High - Essential for user communication

**Tasks:**
- [ ] Integrate trip creation confirmation emails
  - Trigger email after successful itinerary generation
  - Include trip summary and next steps
  - Add "View Trip" button linking to dashboard
  
- [ ] Implement M-Pesa payment receipts
  - Send email immediately after successful payment
  - Include transaction ID, amount, date
  - Add PDF receipt attachment
  
- [ ] Add booking confirmation emails
  - Send when user saves/books a trip
  - Include full itinerary details
  - Add calendar invite attachment
  
- [ ] Fix password reset email flow
  - Create custom password reset form
  - Override Django default to use EmailService
  - Ensure emails are logged in EmailLog

**Dependencies:** None (email system already built)

---

### 1.2 Payment Features
**Status:** M-Pesa works, missing receipt/history
**Estimated Time:** 3-4 days
**Impact:** High - Required for transparency

**Tasks:**
- [ ] Payment receipts (email + PDF)
  - Generate PDF receipt after payment
  - Include: Transaction ID, amount, date, payment method
  - Email PDF to user
  - Store PDF in S3 (when migrated to AWS)
  
- [ ] Payment history page
  - Create `/payments/history/` view
  - List all user transactions
  - Show: Date, amount, status, receipt download
  - Add filters: Date range, status, payment method
  
- [ ] Transaction status tracking
  - Real-time status updates (pending, completed, failed)
  - Webhook handler for M-Pesa callbacks
  - Update transaction status in database
  - Send status change notifications
  
- [ ] Refund handling (future)
  - Admin interface to process refunds
  - Automatic refund emails
  - Update transaction status

**Dependencies:** Email notifications (for receipts)

---

### 1.3 User Dashboard Enhancements
**Status:** Basic dashboard exists
**Estimated Time:** 4-5 days
**Impact:** High - Core user experience

**Tasks:**
- [ ] View saved itineraries
  - List all user trips on dashboard
  - Show: Destination, dates, status, thumbnail
  - Sort by: Date created, trip date, status
  - Pagination (10 trips per page)
  
- [ ] Edit existing trips
  - "Edit" button on each trip
  - Redirect to wizard with pre-filled data
  - Update existing itinerary instead of creating new
  - Show "Last updated" timestamp
  
- [ ] Delete trips
  - "Delete" button with confirmation modal
  - Soft delete (mark as deleted, don't remove from DB)
  - Option to permanently delete after 30 days
  
- [ ] Download itinerary as PDF
  - "Download PDF" button on trip detail page
  - Professional PDF template
  - Include: Itinerary, costs, map, contacts
  - Store generated PDFs in S3
  
- [ ] Share trip via link
  - "Share" button generates public link
  - Copy link to clipboard
  - View count tracking
  - Option to make trip private again
  
- [ ] Payment history section
  - Dedicated tab for payments
  - Link to payment history page
  - Show recent transactions

**Dependencies:** Payment history, Itinerary sharing

---

## Priority 2: Important Features (Build Next)

### 2.1 Itinerary Sharing
**Status:** Share code exists, no UI
**Estimated Time:** 2-3 days
**Impact:** Medium-High - Viral growth potential

**Tasks:**
- [ ] Public share page
  - Create `/trips/shared/<share_code>/` view
  - Display full itinerary (read-only)
  - Show: Destinations, schedule, costs, photos
  - "Create My Own Trip" CTA button
  - Track views (increment view_count)
  
- [ ] Social media sharing buttons
  - Add share buttons: WhatsApp, Facebook, Twitter, Email
  - Generate preview cards (Open Graph tags)
  - Include trip image and description
  
- [ ] Copy link functionality
  - "Copy Link" button
  - Toast notification on copy
  - Share link format: `https://safarismart.co.ke/trips/shared/abc123`

**Dependencies:** None

---

### 2.2 Trip Management
**Status:** Not implemented
**Estimated Time:** 3-4 days
**Impact:** Medium - User convenience

**Tasks:**
- [ ] Edit existing trips (covered in Dashboard 1.3)
  
- [ ] Delete trips (covered in Dashboard 1.3)
  
- [ ] Duplicate/clone trips
  - "Duplicate" button on trip detail
  - Create copy with "(Copy)" suffix
  - Allow editing before saving
  - Useful for similar trips
  
- [ ] Mark trips as completed
  - "Mark as Completed" button
  - Change status to "completed"
  - Move to "Past Trips" section
  - Option to rate/review after completion

**Dependencies:** Dashboard enhancements

---

### 2.3 Search & Filters
**Status:** Not implemented
**Estimated Time:** 3-4 days
**Impact:** Medium - Improves discovery

**Tasks:**
- [ ] Search destinations by name/location
  - Search bar on destinations page
  - Real-time search (AJAX)
  - Search by: Name, location, description
  - Highlight search terms in results
  
- [ ] Filter by price range
  - Slider: Min - Max price per day
  - Update results dynamically
  - Show price range in filter UI
  
- [ ] Filter by activities
  - Checkboxes: Wildlife, Beach, Culture, Adventure, etc.
  - Multi-select (AND/OR logic)
  - Show activity icons on cards
  
- [ ] Filter by season/weather
  - Best time to visit
  - Current weather conditions
  - Seasonal recommendations
  
- [ ] Filter by destination type
  - Safari, Beach, Mountain, City, etc.
  - Radio buttons or tabs
  - Update URL with filters (bookmarkable)

**Dependencies:** None

---

## Priority 3: Enhancement Features (Build Later)

### 3.1 User Reviews & Ratings
**Status:** Not implemented
**Estimated Time:** 4-5 days
**Impact:** Medium - Social proof

**Tasks:**
- [ ] Rate destinations
  - 5-star rating system
  - Rate after trip completion
  - Average rating displayed on cards
  - Rating breakdown (5★, 4★, etc.)
  
- [ ] Write reviews
  - Text review (500 char limit)
  - Optional photo upload
  - Review moderation (admin approval)
  - Edit/delete own reviews
  
- [ ] View other user reviews
  - Reviews section on destination detail
  - Sort by: Most recent, highest rated
  - Helpful votes (upvote/downvote)
  - Report inappropriate reviews

**Dependencies:** Trip completion status

---

### 3.2 Admin Analytics Dashboard
**Status:** Basic admin exists
**Estimated Time:** 3-4 days
**Impact:** Medium - Business insights

**Tasks:**
- [ ] Analytics dashboard
  - Total users, trips, revenue
  - Charts: Users over time, revenue trends
  - Popular destinations
  - Conversion funnel
  
- [ ] User management
  - List all users
  - View user details and trips
  - Ban/suspend users
  - Send bulk emails
  
- [ ] Content moderation
  - Review pending reviews
  - Approve/reject user content
  - Flag inappropriate content
  
- [ ] Revenue reports
  - Daily/weekly/monthly revenue
  - Payment method breakdown
  - Export to CSV/PDF
  - Tax reports

**Dependencies:** Payment history, Reviews

---

## Priority 4: Advanced Features (Future)

### 4.1 Booking System
**Status:** Not planned yet
**Estimated Time:** 2-3 weeks
**Impact:** High - Revenue generation

**Tasks:**
- [ ] Book accommodations
  - Integration with booking APIs
  - Hotel/lodge listings
  - Availability calendar
  - Secure payment processing
  
- [ ] Book tours/activities
  - Tour operator listings
  - Activity packages
  - Group bookings
  - Instant confirmation
  
- [ ] Integration with tour operators
  - Partner API integrations
  - Commission tracking
  - Booking management
  - Customer support

**Dependencies:** Payment system, Email notifications

---

### 4.2 Social Features
**Status:** Not planned yet
**Estimated Time:** 2-3 weeks
**Impact:** Low-Medium - Community building

**Tasks:**
- [ ] Follow other users
  - Follow/unfollow functionality
  - View follower/following lists
  - Activity feed from followed users
  
- [ ] Like/save trips
  - Heart icon to save trips
  - "Saved Trips" collection
  - Share saved trips
  
- [ ] Comments on shared trips
  - Comment section on public trips
  - Reply to comments
  - Like comments
  - Moderation

**Dependencies:** User profiles, Itinerary sharing

---

## Implementation Timeline

### Phase 1: Core Functionality (Weeks 1-3)
**Goal:** Complete essential features for MVP

- Week 1: Email Notifications (1.1)
- Week 2: Payment Features (1.2)
- Week 3: Dashboard Enhancements (1.3)

**Deliverables:**
- Users receive trip and payment emails
- Payment history and receipts available
- Full trip management from dashboard

---

### Phase 2: User Experience (Weeks 4-6)
**Goal:** Improve usability and engagement

- Week 4: Itinerary Sharing (2.1)
- Week 5: Trip Management (2.2)
- Week 6: Search & Filters (2.3)

**Deliverables:**
- Users can share trips publicly
- Advanced trip management features
- Easy destination discovery

---

### Phase 3: Growth Features (Weeks 7-9)
**Goal:** Drive engagement and retention

- Week 7: Reviews & Ratings (3.1)
- Week 8: Admin Analytics (3.2)
- Week 9: Testing & Bug Fixes

**Deliverables:**
- Social proof through reviews
- Business insights dashboard
- Stable, polished product

---

### Phase 4: Monetization (Weeks 10+)
**Goal:** Revenue generation

- Booking system integration
- Partner integrations
- Social features

**Deliverables:**
- Direct booking capability
- Commission revenue
- Active community

---

## Success Metrics

### Phase 1 Metrics:
- Email open rate > 40%
- Payment completion rate > 80%
- Dashboard engagement > 60%

### Phase 2 Metrics:
- Share rate > 15%
- Trip edit rate > 25%
- Search usage > 50%

### Phase 3 Metrics:
- Review submission rate > 20%
- Admin dashboard usage daily
- User retention > 40%

### Phase 4 Metrics:
- Booking conversion > 5%
- Revenue growth > 20% MoM
- Social engagement > 30%

---

## Technical Debt & Maintenance

### Ongoing Tasks:
- [ ] Security updates (monthly)
- [ ] Performance optimization
- [ ] Database backups (automated)
- [ ] Monitoring and logging
- [ ] Bug fixes and patches
- [ ] User feedback implementation

---

## Notes

- Priorities may shift based on user feedback
- Timeline estimates are approximate
- Each feature should include tests
- Documentation updated with each release
- AWS migration planned after Phase 1 completion

---

## Version History

- v1.0 (Dec 5, 2025): Initial roadmap created
