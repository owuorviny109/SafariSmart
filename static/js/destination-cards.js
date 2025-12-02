/**
 * Destination Card Interactions
 * Handles keyboard (Enter/Space/Esc), touch, and accessibility enhancements
 */

(function () {
  'use strict';

  const CARD_CLASS = 'destination-card';
  const TOGGLED_CLASS = 'toggled';

  // Initialize destination cards
  function initDestinationCards() {
    const cards = document.querySelectorAll(`.${CARD_CLASS}`);

    if (cards.length === 0) return;

    cards.forEach((card) => {
      // Keyboard interaction
      card.addEventListener('keydown', handleCardKeydown);

      // Touch interaction (for mobile)
      card.addEventListener('touchend', handleCardTouchEnd, { passive: false });
    });

    // Close toggled cards when clicking outside
    document.addEventListener('click', handleDocumentClick);
    document.addEventListener('touchend', handleDocumentClick, { passive: true });
  }

  /**
   * Handle keyboard events on destination cards
   * Enter/Space: Toggle overlay reveal
   * Escape: Close overlay if open
   */
  function handleCardKeydown(event) {
    const card = event.currentTarget;

    // Enter or Space key
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      card.classList.toggle(TOGGLED_CLASS);
    }
    // Escape key
    else if (event.key === 'Escape') {
      card.classList.remove(TOGGLED_CLASS);
    }
  }

  /**
   * Handle touch events on destination cards
   * First tap: Toggle overlay reveal
   * Second tap/link click: Navigate (if CTA link is tapped)
   */
  function handleCardTouchEnd(event) {
    const card = event.currentTarget;
    const isCardToggled = card.classList.contains(TOGGLED_CLASS);

    // If card is not yet toggled, prevent navigation and toggle overlay
    if (!isCardToggled) {
      event.preventDefault();
      card.classList.add(TOGGLED_CLASS);
    }
    // If card is already toggled, allow the tap to proceed
    // (e.g., if user taps on CTA link, let the navigation happen)
  }

  /**
   * Close all toggled cards when clicking/tapping outside
   */
  function handleDocumentClick(event) {
    const clickedCard = event.target.closest(`.${CARD_CLASS}`);

    // If click is outside any destination card, close all toggled ones
    if (!clickedCard) {
      document.querySelectorAll(`.${CARD_CLASS}.${TOGGLED_CLASS}`).forEach((card) => {
        card.classList.remove(TOGGLED_CLASS);
      });
    }
  }

  /**
   * Accessibility: Announce card information to screen readers
   */
  function enhanceA11y() {
    const cards = document.querySelectorAll(`.${CARD_CLASS}`);
    cards.forEach((card) => {
      // Ensure card is keyboard focusable
      if (!card.hasAttribute('tabindex')) {
        card.setAttribute('tabindex', '0');
      }

      // Add aria-pressed state for togglable overlay (optional, for advanced screen readers)
      if (!card.hasAttribute('aria-pressed')) {
        card.setAttribute('aria-pressed', 'false');
      }

      // Update aria-pressed when toggled
      const originalToggle = card.classList.toggle.bind(card.classList);
      card.classList.toggle = function (className) {
        const result = originalToggle(className);
        if (className === TOGGLED_CLASS) {
          card.setAttribute('aria-pressed', card.classList.contains(TOGGLED_CLASS));
        }
        return result;
      };
    });
  }

  /**
   * Prevent interaction on cards if JavaScript is disabled
   * (CSS :hover will still work as fallback)
   */
  function markJSEnabled() {
    document.documentElement.setAttribute('data-js-enabled', 'true');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initDestinationCards();
      enhanceA11y();
      markJSEnabled();
    });
  } else {
    initDestinationCards();
    enhanceA11y();
    markJSEnabled();
  }

  // Re-initialize on dynamic content updates (e.g., AJAX loads)
  window.addEventListener('destination-cards:reinit', () => {
    initDestinationCards();
    enhanceA11y();
  });
})();
