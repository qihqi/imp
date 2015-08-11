var ProdBox = React.createClass({
  getInitialState: function() {
    return {"name_es": 2, "name_zh": 2};
  },
  handler: function(event) {
    alert(event.target.ref);
  },
  render: function() {
    var prodrefs = ["name_es", "name_zh"];
    alert(this.state);
    var values = prodrefs.map(function(name) {
      return (
        <p>
        {name}: <input name={name} ref={name} value={this.state[name]} onChange={this.handler}/>
        </p>
      );
    }.bind(this));
    return (<div class="product">
      {values}
    </div>);
  }
});
