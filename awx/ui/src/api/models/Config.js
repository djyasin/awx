import Base from '../Base';

class Config extends Base {
  constructor(http) {
    super(http);
    this.baseUrl = 'api/v2/config/';
    this.read = this.read.bind(this);
  }

  readSubscriptions(clientId, clientSecret) {
    return this.http.post(`${this.baseUrl}subscriptions/`, {
      subscriptions_client_id: clientId,
      subscriptions_client_secret: clientSecret,
    });
  }

  attach(data) {
    return this.http.post(`${this.baseUrl}attach/`, data);
  }
}

export default Config;
