var ProdBox = React.createClass({
  getInitialState: function() {
    return {"name_es": 2, "name_zh": 2};
  },
  handler: function(key, event) {
    alert(event.target.value);
    alert(event.target.name);
    this.setState({key: event.target.value});
  },
  render: function() {
    var prodrefs = ["name_es", "name_zh"];
    var values = prodrefs.map(function(name) {
      return (
        <p>
        {name}: <input name={name} ref={name} value={this.state[name]} onChange={this.handler.bind(this, name)}/>
        </p>
      );
    }.bind(this));
    return (<div class="product">
      {values}
    </div>);
  }
});
