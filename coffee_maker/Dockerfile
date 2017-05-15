FROM %%BASE_IMAGE%%

# Add version
ENV LANG C.UTF-8

# Setup base
RUN apk add --no-cache jq

# Copy data
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
