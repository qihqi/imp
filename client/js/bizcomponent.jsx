'use strict';
var comp = require('./components.jsx');

const PROD_KEYS = [
    "name_es",
    "name_zh",
    "providor_zh",
    "providor_item_id",
    "declaring_id"];

function render_input_for_keys(keys, classes) {
    return function() {
        var values = keys.map(function(name) {
            return (
                <p>
                {name}:
                <input name={name} ref={name}
                value={this.state[name]}
                onChange={this.handler.bind(this, name)}/>
                </p>
                );
        }.bind(this));
        return (<div class={classes}>
            {values}
            </div>);
    }
}

function fetch_and_set_content(baseurl, callback) {
    return function(uid) {
        var url = baseurl + uid;
        $.ajax({
            url: url,
            success: function(data) {
                console.log(data);
                console.log(callback);
                callback(data);
            }.bind(this)
        });
    }
}

function setState(x) {
    this.setState(x);
}

function displaylist(names, content) {
    var lists =content.map(function(i) {
        var innerhtml = '';
        for (var x in names) {
            innerhtml += (' ' + i[names[x]]);
        }
        return <li> {innerhtml} </li>;
    });
    return (<ul>{lists}</ul>);
}

var ProdList2 = React.createClass({

    render: function() {
        var click = this.props.click;
        var makerow = function(prod) {
            var clickhandler = function() {
                console.log('click logger');
                console.log(prod);
                click(prod.upi);
            };
            return (<tr key={prod.uid}>
                <td><button onClick={clickhandler}>edit</button></td>
                <td>{prod.name_es}</td>
                <td>{prod.name_zh}</td>
                <td>{prod.providor_zh}</td>
                <td>{prod.providor_item_id}</td>
                <td>{prod.declared_id}</td>
            </tr>);
        }

        var rows = this.props.list.map(makerow);

        return (
            <div> Hello
            <table className="table">
            <tr>
                <th>#</th>
                <th>name_es</th>
                <th>name_zh</th>
                <th>providor_zh</th>
                <th>providor_item_id</th>
                <th>declared_id</th>
            </tr>
            <tbody>
            {rows}
            </tbody>
            </table>
            </div>);
    }
});
 

var ShowProd = React.createClass({
    setCurrent: function(current) {
        this.setState({current: current});
    },
    getAllProd: function() {
        $.ajax({
            url: '/importapi/prod',
            success: function(result) {
                this.setState({list: result.result});
            }.bind(this)
        }); 
    },
    getInitialState: function() {
        this.getAllProd();
        return {
            current: 1,
            list: []
        }
    },
    editProd: function(x) {
        this.setState({current: x}, function() {
            this.refs.editbox.fetchnew();
        }.bind(this));
    },
    editedProd: function(newprod) {
        var newlist = this.state.list.slice();
        for (var i in newlist) {
            if (newlist[i].upi == newprod.upi) {
                newlist[i] = newprod;
            }
        }
        this.setState({'list': newlist});
    },
    render: function() {
        return (<div className="container">
            <div className="row" >
            <div className="col-md-4">
                <div className="myfloat">
                    <comp.CreateOrUpdateBox url="/importapi/prod" ref="editbox"
                      names={PROD_KEYS} update={true} uid={this.state.current}
                      callback={this.editedProd}/>
                </div>
            </div>
            <div className="col-md-8">
                <ProdList2 list={this.state.list} click={this.editProd}/>
            </div>
            </div>
        </div>);
    }
});


var Declared = React.createClass({
    fetchcontent: fetch_and_set_content('/importapi/declared/',
        function(x) { this.setState(x) }.bind(this)),
    altercontent: function(){
        var url = '/importapi/declared/' + this.props.params.uid;
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.state),
            success: function(data) {
                alert('success');
            }
        });
    },
    submit: function(e) {
        e.preventDefault();
        this.altercontent();
    },
    getInitialState: function() {
        if (typeof this.props.uid !== 'undefined') {
            this.fetchcontent(this.props.params.uid, setState.bind(this));
        }
        return {"display_name": 2, "display_price": 2};
    },
    handler: function(key, event) {
        var newstate = {};
        newstate[event.target.name] = event.target.value;
        this.setState(newstate);
    },
    render: function() {
        return (<form onSubmit={this.submit}>
            {render_input_for_keys(["display_name", "display_price"]).bind(this)()}
            <input type="submit"/>
            </form>);
    }
});

var ProdBox = React.createClass({
    fetchcontent: function(x, callback) {
        fetch_and_set_content('/importapi/prod/', callback)(x);
    },
    altercontent: function(){
        console.log(this.state);
        var url = '/importapi/prod/' + this.props.params.uid;
        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(this.state),
            success: function(data) {
                alert('success');
            }
        });
    },
    submit: function(e) {
        e.preventDefault();
        this.altercontent();
    },
    getInitialState: function() {
        this.fetchcontent(this.props.params.uid, setState.bind(this));
        return {"name_es": 2, "name_zh": 2};
    },
    handler: function(key, event) {
        var newstate = {};
        newstate[event.target.name] = event.target.value;
        this.setState(newstate);
    },
    delete: function() {
        console.log(this.state);
        var url = '/importapi/prod/' + this.props.params.uid;
        $.ajax({
            url: url,
            method: 'DELETE',
            success: function(data) {
                alert('success');
            }
        });
    },
    render: function() {
        return (<form onSubmit={this.submit}>
                {render_input_for_keys(PROD_KEYS).bind(this)()}
                <input type="submit"/>
                <button onClick={this.delete}>Delete</button>
            </form>);
    }
});

var PurchaseHeader = React.createClass({
    getInitialState: function() {
        this.fetchcontent(this.props.uid, setState.bind(this));
        return {uid: 1, total_rmb: 100};
    },
    handler: function(key, event) {
    },
    fetchcontent: fetch_and_set_content('/importapi/purchase/', setState.bind(this)),
    render: render_input_for_keys(['timestamp', 'uid', 'total_rmb', 'providor'])
});

var Purchase = React.createClass({
    getInitialState: function() {
        this.fetchcontent();
        return {items: []};
    },
    fetchcontent: function() {
        var url = '/importapi/purchase/' + this.props.params.uid;
        $.ajax({
            url: url,
            success: function(data) {
                this.setState(data);
            }.bind(this)
        });
    },
    render: function() {
        var all_rows = this.state.items.map(function(i) {
            return (<tr>
                <td>{i.name_zh}</td>
                <td>{i.name_es}</td>
                <td>{i.providor_zh}</td>
                <td>{i.providor_item_id}</td>
                <td>{i.color}</td>
                <td>{i.quantity}</td>
                <td>{i.price_rmb}</td>
                <td>{i.quantity * i.price_rmb}</td>
                <td><a href={"#prod/" + i.upi}>View</a></td>
            </tr>);
        });
        return (
            <div className="container">
            <PurchaseHeader uid={this.props.params.uid} />
            <table className="table">
                <tr>
                    <td>{"名称"}</td>
                    <td>Nombre</td>
                    <td>{"供货商"}</td>
                    <td>{"供货商 货号"}</td>
                    <td>{"颜色"}</td>
                    <td>{"数量"}</td>
                    <td>{"价格"}</td>
                    <td>{"总价"}</td>
                    <td></td>
                </tr>
                {all_rows}
            </table>
            </div>
        );
    }
});


var ProdList = React.createClass(comp.display_list_of_item(PROD_KEYS));

var Test = React.createClass({
    render: function() {
        return <comp.CreateOrUpdateBox url='/importapi/declaredgood' names={["display_name", "display_price"]} />
    }
});

var DeclaredUI = React.createClass({
    render: function() {
        return <DeclaredItem uid={this.props.params.uid} />
    }
});

var DeclaredItem = React.createClass({
    fetchcontent: function() {
        fetch_and_set_content('/importapi/declaredgood/',
            setState.bind(this))(this.props.uid);
        fetch_and_set_content('/importapi/prod?declaring_id=',
            function(result) {
                this.setState({'prods': result.result});
            }.bind(this))(this.props.uid);
    },
    getInitialState: function() {
        this.fetchcontent();
        return {display_price: '', display_name: '', prods: []};
    },
    render: function() {
        return (<div>
            <p>{this.state.display_name} {this.state.display_price}</p>
            <ProdList list={this.state.prods} />
        </div>);
    }
});

module.exports.Purchase = Purchase;
module.exports.DeclaredItem = DeclaredItem;

window.Purchase = Purchase;
window.DeclaredUI = DeclaredUI;
window.Test = Test;
window.ProdBox = ProdBox;
window.ProdList = ProdList;
window.ProdList2 = ProdList2;
window.ShowProd= ShowProd;
