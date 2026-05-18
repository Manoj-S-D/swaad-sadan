# Feature Implementation Plan

## ✅ COMPLETED - Database Schema
- Added `order_comments` table for ratings and feedback
- Added `user_addresses` table for saved locations
- Supports both SQLite and PostgreSQL

## 🚀 PRIORITY 1 - Core Features (Implementing Now)

### 1. Order Comments & Rating System
**Files to modify:**
- `backend-python/routes/orders.py` - Add comment endpoints
- `backend-python/templates/admin_orders.html` - Show comments & reply interface
- `backend-python/templates/orders.html` - Customer comment form

**Endpoints needed:**
- `POST /api/orders/<order_id>/comment` - Add comment/rating
- `GET /api/orders/<order_id>/comments` - Get comments
- `PUT /api/orders/comments/<comment_id>/reply` - Admin reply

### 2. Fix Payment Method Display
**Issue:** Shows "online" for both COD and online payments
**Fix:** Update payment object to store actual method (UPI, card, wallet, etc.)
**Files:** `backend-python/routes/orders.py`, `backend-python/templates/cart.html`

### 3. Admin Order Cancellation with Refund
**Files:**
- `backend-python/templates/admin_orders.html` - Add cancel button with refund
- `backend-python/routes/orders.py` - Update cancellation logic
**Requirements:** Show payment ID/RRN for refund processing

### 4. Saved Delivery Addresses
**Files:**
- `backend-python/routes/auth.py` - Add address CRUD endpoints  
- `backend-python/templates/profile.html` - Address management UI
- `backend-python/templates/cart.html` - Address selector

### 5. Search Functionality
**Add to:**
- Admin orders page
- Admin products page
- Admin users page
- Customer orders page

## 📋 PRIORITY 2 - Enhanced Features

### 6. Payment Method Details
- Capture from Razorpay payment response
- Show in admin panel: UPI ID, card last 4 digits, wallet name

### 7. Google Maps Integration
- Add location picker widget
- Save lat/long with addresses
- Show delivery location on map

## 🔔 PRIORITY 3 - Advanced Features (Future)

### 8. Real-time Notifications
- WebSocket or Server-Sent Events
- Notification bell icon
- Notification center
- Push notifications

### 9. Advanced Search
- Full-text search across all fields
- Filters and sorting
- Export results

## 📝 Implementation Status

| Feature | Status | Priority |
|---------|--------|----------|
| Database Schema | ✅ Complete | P1 |
| Order Comments API | 🔄 In Progress | P1 |
| Admin Reply | ⏳ Pending | P1 |
| Payment Method Fix | ⏳ Pending | P1 |
| Admin Cancel/Refund | ⏳ Pending | P1 |
| Saved Addresses | ⏳ Pending | P1 |
| Search Functionality | ⏳ Pending | P1 |
| Payment Details | ⏳ Pending | P2 |
| Google Maps | ⏳ Pending | P2 |
| Notifications | ⏳ Pending | P3 |
