package com.stocktrum.backend.features.auth.domain;

public record AccessAndRefreshTokens(String accessToken, RefreshToken refreshToken) {}
