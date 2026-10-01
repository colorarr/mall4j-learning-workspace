FROM eclipse-temurin:17-jre-jammy


RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN mkdir -p /opt/projects/mall4j

WORKDIR /opt/projects/mall4j

ADD ./yami-shop-admin/target/yami-shop-admin-0.0.1-SNAPSHOT.jar ./

EXPOSE 8080

ENTRYPOINT ["java", "-Xms256m", "-Xmx768m", "-Xss256k", "-XX:SurvivorRatio=8", "-Dspring.profiles.active=docker", "-jar", "yami-shop-admin-0.0.1-SNAPSHOT.jar"]
