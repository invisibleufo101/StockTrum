package com.stocktrum.backend.features.auth.service;

import com.stocktrum.backend.features.auth.domain.PasswordResetToken;
import com.stocktrum.backend.features.auth.repo.PasswordResetTokenRepository;
import com.stocktrum.backend.features.user.domain.User;
import com.stocktrum.backend.features.user.repo.UserRepository;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.SecureRandom;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;

@Service
public class PasswordResetService {
  private final UserRepository userRepository;
  private final PasswordResetTokenRepository passwordResetTokenRepository;
  private final JavaMailSender mailSender;
  private final PasswordEncoder encoder;

  private static final SecureRandom RNG = new SecureRandom();
  private static final Base64.Encoder B64 = Base64.getUrlEncoder().withoutPadding();
  private static final Duration TTL = Duration.ofMinutes(30);
  private static final int SELECTOR_BYTES = 9;
  private static final int VALIDATOR_BYTES = 32;

  public PasswordResetService(
      UserRepository users,
      PasswordResetTokenRepository tokens,
      PasswordEncoder encoder,
      JavaMailSender mailSender) {
    this.userRepository = users;
    this.passwordResetTokenRepository = tokens;
    this.mailSender = mailSender;
    this.encoder = encoder;
  }

  /**
   * Generates and stores a password reset token for the given email, and sends the reset link via
   * email.
   *
   * <p>If the email does not exist, nothing happens (prevents account enumeration).
   *
   * @param email user email requesting password reset
   */
  @Transactional
  public void requestReset(String email) {
    userRepository
        .findByEmail(email)
        .ifPresent(
            user -> {
              String selector = randomBase64Url(SELECTOR_BYTES);
              String validator = randomBase64Url(VALIDATOR_BYTES);

              Instant now = Instant.now();
              //      String token = generateToken();
              PasswordResetToken prt = new PasswordResetToken();
              prt.setRequestedAt(now);
              prt.setUser(user);
              prt.setSelector(selector);
              prt.setValidatorHash(encoder.encode(validator));
              prt.setExpiresAt(now.plus(TTL));
              passwordResetTokenRepository.save(prt);
              String combined = selector + "." + validator;
              sendEmail(user.getEmail(), combined); // link carries the raw token
            });
  }

  /**
   * Verifies the provided reset token, updates the user's password, increments token version to
   * revoke old sessions, and marks the reset token as used.
   *
   * @param combinedToken token in the format "selector.validator"
   * @param newPassword new raw password
   */
  @Transactional
  public void reset(String combinedToken, String newPassword) {
    String[] parts = combinedToken.split("\\.", 2);

    String selector = parts[0];
    String validator = parts[1];

    PasswordResetToken prt =
        passwordResetTokenRepository
            .findBySelector(selector)
            .filter(t -> !t.isUsed() && t.getExpiresAt().isAfter(Instant.now()))
            .orElseThrow();

    if (!encoder.matches(validator, prt.getValidatorHash())) {
      throw new BadCredentialsException("");
    }

    User user = prt.getUser();
    user.setPassword(encoder.encode(newPassword));
    user.setTokenVersion(user.getTokenVersion() + 1);
    userRepository.save(user);

    prt.setUsed(true);
    passwordResetTokenRepository.save(prt);
  }

  /**
   * Sends the password reset email linking to the frontend reset page.
   *
   * @param to target email
   * @param combinedToken selector + validator string
   */
  private void sendEmail(String to, String combinedToken) {
    String url = "https://your-frontend/reset-password?token=" + combinedToken;
    SimpleMailMessage msg = new SimpleMailMessage();
    msg.setFrom("agallego1112@gmail.com");
    msg.setTo(to);
    msg.setSubject("Password Reset");
    msg.setText("Click to reset your password:\n" + url);
    mailSender.send(msg);
  }

  private static String randomBase64Url(int numBytes) {
    byte[] buf = new byte[numBytes];
    new SecureRandom().nextBytes(buf);
    return Base64.getUrlEncoder().withoutPadding().encodeToString(buf);
  }
}
