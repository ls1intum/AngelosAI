# ============================
# 1) Build Stage
# ============================
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the rest of the project
COPY . .

# Build the project without running tests
RUN mvn clean package -DskipTests

# ============================
# 2) Run Stage
# ============================
FROM eclipse-temurin:17-jdk-jammy
WORKDIR /app

# Copy the built jar from the 'build' stage
COPY --from=build /app/target/angelos-kb-backend-0.0.1-SNAPSHOT.jar /app/app.jar

# Expose the Spring Boot port
EXPOSE 9007

# Default entrypoint
ENTRYPOINT ["java", "-jar", "/app/app.jar"]